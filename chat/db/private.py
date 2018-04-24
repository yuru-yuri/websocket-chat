from . import BaseDb


class Private(BaseDb):
    """
    Private user-to-user messages
    """
    def make_schema(self):
        self.execute("""
                CREATE TABLE private (
                    `user`	UNSIGNEDBIGINT,
                    `message`	TEXT,
                    `on_message`	INTEGER,
                    `date`	datetime,
                    PRIMARY KEY(user)
                )
            """)

    def get_messages(self):
        return self.query("""
            SELECT rowid, * FROM messages
            LIMIT 100 ORDER BY date DESC 
        """)
