from __future__ import annotations
import os
from getpass import getpass
from typing import Optional

from django.core.management.base import BaseCommand
from django_ldap3_auth.backends import LDAPBackend
from django_ldap3_auth.conf import from_django_settings
from django_ldap3_auth.models import LDAPConfig
from ldap3 import Server, Connection, ALL, SUBTREE, Tls


MASK = '********'


def _mask(v: Optional[str]) -> str:
    if not v:
        return ''
    if '@' in v:
        u, _, d = v.partition('@')
        return f"{u[:2]}***@{d}"
    return v[:2] + '***'


class Command(BaseCommand):
    help = 'Диагностика LDAP/AD: проверка bind, поиск DN по username и попытка входа.'

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True, help='Имя пользователя для проверки (sAMAccountName или userPrincipalName)')
        parser.add_argument('--password', nargs='?', help='Пароль пользователя (лучше не указывать в CLI)')
        parser.add_argument('--debug', action='store_true', help='Печать подробных результатов ldap3')

    def handle(self, *args, **opts):
        username = opts['username']
        password = opts['password'] or getpass(f'Введите пароль для {username}: ')
        debug = bool(opts['debug'])

        # 1) Сбор итоговой конфигурации
        conf = from_django_settings()
        if getattr(conf, 'use_db_config', False):
            conf = LDAPConfig.to_conf(conf)

        self.stdout.write(self.style.NOTICE('— Конфигурация —'))
        self.stdout.write(f"HOST: {conf.host}:{conf.port}  SSL: {conf.use_ssl}")
        self.stdout.write(f"BASE_DN: {conf.base_dn}")
        self.stdout.write(f"BIND_DN: {_mask(conf.bind_dn)}  BIND_PASSWORD: {MASK if conf.bind_password else ''}")
        self.stdout.write(f"SEARCH_FILTER: {conf.search_filter}")
        self.stdout.write(f"SEARCH_ATTRS: {conf.search_attrs}")

        # 2) Пробуем bind сервисной учёткой (если задана)
        try:
            server = Server(conf.host, port=conf.port, use_ssl=conf.use_ssl, get_info=ALL)
            if conf.bind_dn:
                conn = Connection(server, user=conf.bind_dn, password=conf.bind_password, auto_bind=True)
            else:
                conn = Connection(server, auto_bind=True)  # анонимный (редко разрешён)
            if debug:
                self.stdout.write(f"[bind svc] result: {conn.result}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка bind сервисной учёткой: {e}"))
            return

        # 3) Поиск DN пользователя: пробуем расширенный фильтр
        # Если пользователь ввёл UPN, полезно искать по (|(userPrincipalName=...)(sAMAccountName=...))
        if '@' in username:
            sf = f"(&{conf.search_filter.strip(')')}(userPrincipalName={username})(|(userPrincipalName={username})(sAMAccountName={username.split('@')[0]})))"
        else:
            sf = conf.search_filter.format(username=username)
            # Универсальная OR-версия
            sf = f"(|{sf}(userPrincipalName={username}))"

        if not conn.search(conf.base_dn, sf, SUBTREE, attributes=conf.search_attrs):
            if debug:
                self.stdout.write(f"[search] result: {conn.result}")
            self.stdout.write(self.style.ERROR('Пользователь не найден по фильтру. Проверь BASE_DN и SEARCH_FILTER.'))
            conn.unbind()
            return

        if not conn.entries:
            self.stdout.write(self.style.ERROR('Поиск вернул 0 записей.'))
            conn.unbind(); return

        entry = conn.entries[0]
        user_dn = entry.entry_dn
        self.stdout.write(self.style.SUCCESS(f"Найден DN: {user_dn}"))
        if debug:
            self.stdout.write(f"Атрибуты: {entry.entry_attributes_as_dict}")

        conn.unbind()

        # 4) Пробуем bind как пользователь
        try:
            server = Server(conf.host, port=conf.port, use_ssl=conf.use_ssl, get_info=ALL)
            conn_user = Connection(server, user=user_dn, password=password, auto_bind=True)
            if debug:
                self.stdout.write(f"[bind user] result: {conn_user.result}")
            conn_user.unbind()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Bind пользователем НЕ удался: {e}"))
            self.stdout.write('Возможные причины: неверный пароль, неверный DN, требования к SSL/LDAPS, неправильный хост/порт.')
            return

        # 5) Пытаемся через backend (создание/обновление локального Django пользователя)
        backend = LDAPBackend()
        user = backend.authenticate(None, username=username, password=password)
        if user:
            self.stdout.write(self.style.SUCCESS(f"OK: вошёл как {user.username} (id={user.id})"))
        else:
            self.stdout.write(self.style.ERROR('FAIL на этапе backend.authenticate() — проверь фильтр и маппинг атрибутов.'))
