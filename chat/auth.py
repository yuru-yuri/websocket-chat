import bcrypt


class Auth:
    @staticmethod
    def login(password: str, pass_hash: str):
        return bcrypt.checkpw(password, pass_hash)

    @staticmethod
    def str2hash(val: str):
        return bcrypt.hashpw(val, bcrypt.gensalt())
