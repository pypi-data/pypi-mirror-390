from django.contrib import admin

from .forms import LDAPConfigForm
from .models import LDAPConfig


@admin.register(LDAPConfig)
class LDAPConfigAdmin(admin.ModelAdmin):
    form = LDAPConfigForm
    fieldsets = (
        (None, { 'fields': ('host', 'port', 'use_ssl', 'base_dn') }),
        ('Bind', { 'fields': ('bind_dn', 'bind_password') }),
        ('Поиск', { 'fields': ('search_filter', 'search_attrs') }),
        ('Маппинг', { 'fields': ('default_email_domain', 'map_first_name', 'map_last_name') }),
        ('Группы', { 'fields': ('superuser_group', 'staff_group') }),
    )


    class Media:
        js = ('django_ldap3_auth/ldapconfig.js',)

    def get_readonly_fields(self, request, obj=None):
        # Можно сделать только просмотр (например на проде)
        return super().get_readonly_fields(request, obj)

