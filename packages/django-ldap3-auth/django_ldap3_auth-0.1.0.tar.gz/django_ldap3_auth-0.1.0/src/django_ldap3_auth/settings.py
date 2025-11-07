AUTHENTICATION_BACKENDS = [
    'django_ldap3_auth.backends.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Опциональные настройки LDAP (можно переопределить в админке)
LDAP_USE_DB_CONFIG = True  # Использовать настройки из БД
LDAP_HOST = 'ldap.example.com'
LDAP_PORT = 389
INSTALLED_APPS += [
    # ...
    'django_ldap3_auth',
]
