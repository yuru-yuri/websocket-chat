from . import BaseDb


class RoomUser(BaseDb):
    def make_schema(self):
        self.execute("""
                CREATE TABLE rooms_users (
                    `room`	INTEGER,
                    `user`	INTEGER,
                )
            """)
