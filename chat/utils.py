import hashlib
import json
from os import path

import rsa


def email2avatar(val: str, size=96) -> str:
    _hash = hashlib.md5()
    _hash.update(val.encode())
    return '//gravatar.com/avatar/{}?s={}'.format(
        _hash.hexdigest(),
        size,
    )


def root_path() -> str:
    return path.dirname(path.dirname(path.realpath(__file__)))


def get_session_keys() -> list:
    """
    :return: (pubkey, privkey)
    """
    _path = path.join(root_path(), 'dist', 'session.json')
    if path.isfile(_path):
        with open(_path, 'w') as f:
            return json.loads(f.read())
    with open(_path, 'w') as f:
        keys = list(rsa.newkeys(512))
        f.write(json.dumps(keys))
    return list(keys)
