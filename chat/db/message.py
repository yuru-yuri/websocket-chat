from . import BaseDb


class Message(BaseDb):
    def make_schema(self, path: str):
        self.execute("""
                CREATE TABLE messages (
                    `user`	UNSIGNEDBIGINT,
                    `message`	TEXT,
                    `on_message`	INTEGER,
                    `date`	datetime,
                    PRIMARY KEY(user)
                )
            """)

    def user_messages(self, user_id):
        return self.query("""
            SELECT rowid, * FROM messages
            WHERE user = ? LIMIT 100 ORDER BY date DESC
        """, (user_id,))

    def get_messages(self):
        return self.query("""
            SELECT rowid, * FROM messages
            LIMIT 100 ORDER BY date DESC 
        """)
