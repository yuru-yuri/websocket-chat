import hashlib
from os import path


def email2avatar(val: str, size=96):
    _hash = hashlib.md5()
    _hash.update(val.encode())
    return '//gravatar.com/avatar/{}?s={}'.format(
        _hash.hexdigest(),
        size,
    )


def root_path():
    return path.dirname(path.dirname(path.realpath(__file__)))
