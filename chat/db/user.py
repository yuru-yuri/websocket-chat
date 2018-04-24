from . import BaseDb


class User(BaseDb):
    def __init__(self):
        super().__init__('users.db')

    def make_schema(self, path: str):
        self.execute("""
                CREATE TABLE users (
                    `login`	TEXT,
                    `pass`	TEXT,
                    `email`	TEXT,
                    `token`	TEXT DEFAULT "",
                    `date`	datetime,
                    `online`	INTEGER DEFAULT 0,
                    PRIMARY KEY(login)
                )
            """)

    def get_user(self, login):
        return self.one("""
        SELECT ROWID, *
        FROM users WHERE login = ?
         """, (login, ))
