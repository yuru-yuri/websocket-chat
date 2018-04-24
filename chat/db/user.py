from . import BaseDb


class User(BaseDb):
    def make_schema(self):
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
        SELECT rowid, *
        FROM users WHERE login = ?
         """, (login, ))
