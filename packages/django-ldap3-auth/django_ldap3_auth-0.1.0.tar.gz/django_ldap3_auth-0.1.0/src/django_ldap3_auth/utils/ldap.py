from typing import Optional, Tuple
from ldap3 import Server, Connection, ALL, NTLM, SUBTREE, Tls


def connect(host: str, port: int, use_ssl: bool, bind_dn: Optional[str] = None, bind_password: Optional[str] = None) -> Connection:
    server = Server(host, port=port, use_ssl=use_ssl, get_info=ALL)
    if bind_dn:
        conn = Connection(server, user=bind_dn, password=bind_password, auto_bind=True)
    else:
        conn = Connection(server, auto_bind=True)
    return conn


def search_user(conn: Connection, base_dn: str, search_filter: str, username: str, attributes: list[str]) -> Optional[dict]:
    flt = search_filter.format(username=username)
    if not conn.search(search_base=base_dn, search_filter=flt, search_scope=SUBTREE, attributes=attributes):
        return None
    if not conn.entries:
        return None
    entry = conn.entries[0]
    data = entry.entry_attributes_as_dict
    data['dn'] = entry.entry_dn
    return data


def try_bind(host: str, port: int, use_ssl: bool, dn: str, password: str) -> bool:
    try:
        server = Server(host, port=port, use_ssl=use_ssl, get_info=ALL)
        conn = Connection(server, user=dn, password=password, auto_bind=True)
        conn.unbind()
        return True
    except Exception:
        return False

