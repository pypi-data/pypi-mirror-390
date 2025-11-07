import re
import orjson
import hashlib


def in_list(el):
    return el if isinstance(el, list) else [el]


def to_hash_md5(value: dict | list | tuple | str) -> str:
    return hashlib.md5(orjson.dumps(value, option=orjson.OPT_SORT_KEYS)).hexdigest()


def dsn_hide_password(dsn: str) -> str:
    return re.sub(r':[0-9a-zA-Z].*?@', ':***@', dsn)
