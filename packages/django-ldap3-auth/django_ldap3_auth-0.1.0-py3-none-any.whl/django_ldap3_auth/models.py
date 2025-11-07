from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class LDAPConfig(models.Model):
    singleton = models.BooleanField(default=True, editable=False)

    host = models.CharField(
        max_length=255, default='localhost',
        verbose_name=_('Хост контроллера домена'),
        help_text=_('FQDN или IP контроллера домена (например, dc.example.com).')
    )
    port = models.IntegerField(
        default=389, verbose_name=_('Порт'),
        help_text=_('389 для LDAP, 636 для LDAPS (SSL).')
    )
    use_ssl = models.BooleanField(
        default=False, verbose_name=_('Использовать SSL (LDAPS)'),
        help_text=_('Если включено, будет использоваться LDAPS на порту 636.')
    )
    base_dn = models.CharField(
        max_length=512, blank=True, default='',
        verbose_name=_('Base DN'),
        help_text=_('Корневой DN домена (например, DC=example,DC=com). Будет предложен автоматически на основе хоста.')
    )
    bind_dn = models.CharField(
        max_length=512, blank=True, null=True,
        verbose_name=_('Bind DN (сервисная учётка)'),
        help_text=_('UPN или DN сервисной учётной записи для поиска пользователей (например, ldapuser@example.com).')
    )
    bind_password = models.CharField(
        max_length=512, blank=True, null=True,
        verbose_name=_('Пароль сервисной учётки'),
        help_text=_('Рекомендуется задавать через переменные окружения. Ввод скрыт в админке.')
    )
    search_filter = models.CharField(
        max_length=512,
        default='(|(&(objectClass=user)(sAMAccountName={username}))(&(objectClass=user)(userPrincipalName={username})))',
        verbose_name=_('Фильтр поиска пользователя'),
        help_text=_('Используется для поиска DN пользователя. {username} будет подставлен автоматически.')
    )
    search_attrs = models.JSONField(
        default=list,
        verbose_name=_('Атрибуты для выборки'),
        help_text=_('Список атрибутов AD, которые нужно получать вместе с DN.')
    )
    default_email_domain = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name=_('Домен email по умолчанию'),
        help_text=_('Если у пользователя нет mail в AD — будет сгенерирован username@этот.домен.')
    )
    map_first_name = models.CharField(
        max_length=64, default='givenName',
        verbose_name=_('Атрибут имени (first_name)'),
        help_text=_('Имя поля AD, из которого брать имя пользователя (например, givenName).')
    )
    map_last_name = models.CharField(
        max_length=64, default='sn',
        verbose_name=_('Атрибут фамилии (last_name)'),
        help_text=_('Имя поля AD, из которого брать фамилию пользователя (например, sn).')
    )
    superuser_group = models.CharField(
        max_length=512, blank=True, null=True,
        verbose_name=_('DN группы суперпользователей'),
        help_text=_('Члены этой группы получат права суперпользователя Django.')
    )
    staff_group = models.CharField(
        max_length=512, blank=True, null=True,
        verbose_name=_('DN группы персонала (staff)'),
        help_text=_('Члены этой группы получат доступ к админке (is_staff).')
    )
    class Meta:
        verbose_name = _('LDAP конфигурация')
        verbose_name_plural = _('LDAP конфигурация (одна запись)')

    def clean(self):
        if LDAPConfig.objects.exclude(pk=self.pk).exists():
            raise ValidationError('Допускается только одна запись LDAPConfig.')

    def __str__(self):
        return f"LDAP @ {self.host}:{self.port}"

    @classmethod
    def to_conf(cls, base_conf):
        """Слить base_conf (из settings.py) с записью из БД при наличии."""
        try:
            cfg = cls.objects.get()
        except cls.DoesNotExist:
            return base_conf
        base_conf.host = cfg.host
        base_conf.port = cfg.port
        base_conf.use_ssl = cfg.use_ssl
        base_conf.base_dn = cfg.base_dn
        base_conf.bind_dn = cfg.bind_dn or base_conf.bind_dn
        base_conf.bind_password = cfg.bind_password or base_conf.bind_password
        base_conf.search_filter = cfg.search_filter
        base_conf.search_attrs = cfg.search_attrs or base_conf.search_attrs
        base_conf.default_email_domain = cfg.default_email_domain or base_conf.default_email_domain
        base_conf.map_first_name = cfg.map_first_name or base_conf.map_first_name
        base_conf.map_last_name = cfg.map_last_name or base_conf.map_last_name
        base_conf.superuser_group = cfg.superuser_group or base_conf.superuser_group
        base_conf.staff_group = cfg.staff_group or base_conf.staff_group
        return base_conf
