from __future__ import annotations

from typing import Optional

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.db import transaction

from .conf import from_django_settings
from .models import LDAPConfig
from .utils.ldap import connect, search_user, try_bind


class LDAPBackend(BaseBackend):
    """Аутентификация пользователя через AD/LDAP с авто‑созданием локального Django User."""

    def _get_conf(self):
        conf = from_django_settings()
        if conf.use_db_config:
            conf = LDAPConfig.to_conf(conf)
        return conf

    @staticmethod
    def _first(value):
        if value is None:
            return ''
        if isinstance(value, (list, tuple)):
            return value[0] if value else ''
        return value

    def authenticate(self, request, username: Optional[str] = None, password: Optional[str] = None, **kwargs):
        if not username or not password:
            return None
        conf = self._get_conf()

        # 1) Подключаемся сервисной учёткой для поиска DN пользователя
        try:
            conn = connect(conf.host, conf.port, conf.use_ssl, conf.bind_dn, conf.bind_password)
        except Exception:
            return None

        # 2) Находим DN по фильтру
        # В settings.py задай:
        # LDAP_SEARCH_FILTER = '(|(&(objectClass=user)(sAMAccountName={username}))(&(objectClass=user)(userPrincipalName={username})))'
        data = search_user(conn, conf.base_dn, conf.search_filter, username, conf.search_attrs)
        conn.unbind()
        if not data or 'dn' not in data:
            return None
        user_dn = data['dn']

        # 3) Пробуем bind как сам пользователь
        if not try_bind(conf.host, conf.port, conf.use_ssl, user_dn, password):
            return None

        # 4) Создаём/обновляем локального пользователя Django
        email = None
        if 'mail' in data and data['mail']:
            email = data['mail'][0] if isinstance(data['mail'], list) else data['mail']
        elif conf.default_email_domain:
            email = f"{username}@{conf.default_email_domain}"

        first_name = self._first(data.get(conf.map_first_name))
        last_name  = self._first(data.get(conf.map_last_name))

        with transaction.atomic():
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email or '', 'first_name': first_name or '', 'last_name': last_name or ''},
            )
            changed = False
            if email and user.email != email:
                user.email = email; changed = True
            if first_name and user.first_name != first_name:
                user.first_name = first_name; changed = True
            if last_name and user.last_name != last_name:
                user.last_name = last_name; changed = True

            member_of = data.get('memberOf') or []
            if isinstance(member_of, str):
                member_of = [member_of]

            if conf.superuser_group and conf.superuser_group in member_of:
                if not user.is_superuser:
                    user.is_superuser = True; changed = True
                if not user.is_staff:
                    user.is_staff = True; changed = True
            if conf.staff_group and conf.staff_group in member_of:
                if not user.is_staff:
                    user.is_staff = True; changed = True

            if changed:
                user.save(update_fields=['email', 'first_name', 'last_name', 'is_staff', 'is_superuser'])
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
