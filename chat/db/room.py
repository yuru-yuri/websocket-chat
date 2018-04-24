from . import BaseDb


class Room(BaseDb):
    def make_schema(self):
        self.execute("""
                CREATE TABLE rooms (
                    `title`	TEXT,
                    `owner`	INTEGER,
                )
            """)

    def users(self, rom_id):
        return self.query("""
            SELECT users.rowid, users.* FROM users
            JOIN users.rowid = rooms_users.user
            WHERE rooms_users.room = ?
        """, (rom_id,))
