from django import forms
from django.utils.translation import gettext_lazy as _
from .models import LDAPConfig

class LDAPConfigForm(forms.ModelForm):
    class Meta:
        model = LDAPConfig
        fields = '__all__'
        widgets = {
            'bind_password': forms.PasswordInput(render_value=False, attrs={'autocomplete': 'new-password'}),
        }
        help_texts = {
            'host': _('Например: dc.example.com'),
            'base_dn': _('Например: DC=example,DC=com'),
            'bind_dn': _('Например: admin@example.com'),
        }
        labels = {
            'host': _('Хост контроллера домена'),
            'port': _('Порт'),
            'use_ssl': _('Использовать SSL (LDAPS)'),
            'base_dn': _('Base DN'),
            'bind_dn': _('Bind DN (сервисная учётка)'),
            'bind_password': _('Пароль сервисной учётки'),
            'search_filter': _('Фильтр поиска пользователя'),
            'search_attrs': _('Атрибуты для выборки'),
            'default_email_domain': _('Домен email по умолчанию'),
            'map_first_name': _('Атрибут имени (first_name)'),
            'map_last_name': _('Атрибут фамилии (last_name)'),
            'superuser_group': _('DN группы суперпользователей'),
            'staff_group': _('DN группы персонала (staff)'),
        }
