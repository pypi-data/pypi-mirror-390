from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from django.conf import settings as dj_settings


@dataclass
class Config:
    host: str = 'localhost'
    port: int = 389
    use_ssl: bool = False
    base_dn: str = ''

    bind_dn: str | None = None
    bind_password: str | None = None

    search_filter: str = '(&(objectClass=user)(sAMAccountName={username}))'
    search_attrs: List[str] = field(default_factory=lambda: [
        'cn', 'mail', 'givenName', 'sn', 'memberOf', 'userPrincipalName'
    ])

    default_email_domain: str | None = None
    map_first_name: str = 'givenName'
    map_last_name: str = 'sn'

    superuser_group: Optional[str] = None
    staff_group: Optional[str] = None

    use_db_config: bool = False


def from_django_settings() -> Config:
    c = Config(
        host=getattr(dj_settings, 'LDAP_HOST', 'localhost'),
        port=int(getattr(dj_settings, 'LDAP_PORT', 389)),
        use_ssl=bool(getattr(dj_settings, 'LDAP_USE_SSL', getattr(dj_settings, 'USE_SSL', False))),
        base_dn=getattr(dj_settings, 'LDAP_BASE_DN', getattr(dj_settings, 'BASE_DN', '')),
        bind_dn=getattr(dj_settings, 'LDAP_BIND_DN', getattr(dj_settings, 'USERNAME', None)),
        bind_password=getattr(dj_settings, 'LDAP_BIND_PASSWORD', getattr(dj_settings, 'PASSWORD', None)),
        search_filter=getattr(dj_settings, 'LDAP_SEARCH_FILTER', '(&(objectClass=user)(sAMAccountName={username}))'),
        search_attrs=list(getattr(dj_settings, 'LDAP_SEARCH_ATTRS', ['cn', 'mail', 'givenName', 'sn', 'memberOf', 'userPrincipalName'])),
        default_email_domain=getattr(dj_settings, 'LDAP_DEFAULT_EMAIL_DOMAIN', None),
        map_first_name=getattr(dj_settings, 'LDAP_MAP_FIRST_NAME', 'givenName'),
        map_last_name=getattr(dj_settings, 'LDAP_MAP_LAST_NAME', 'sn'),
        superuser_group=getattr(dj_settings, 'LDAP_SUPERUSER_GROUP', None),
        staff_group=getattr(dj_settings, 'LDAP_STAFF_GROUP', None),
        use_db_config=bool(getattr(dj_settings, 'LDAP_USE_DB_CONFIG', False)),
    )
    return c
