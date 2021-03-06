from . import BaseDb


class Message(BaseDb):
    """
    User-to-room messages
    """
    def make_schema(self):
        self.execute("""
                CREATE TABLE messages (
                    `user`	UNSIGNEDBIGINT,
                    `message`	TEXT,
                    `room`	INTEGER NULL,
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
