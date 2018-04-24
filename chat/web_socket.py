from wsrpc import WebSocket
from time import strftime
from .utils import email2avatar


class ChatWebSocket(WebSocket):
    users = None
    messages = None
    rowid = 0

    def _unresolvable(self, *args, **kwargs):
        pass

    def data_received(self, chunk):
        pass

    @staticmethod
    def time_now():
        return strftime('%Y-%m-%d %H:%M:%S')

    def system_message(self, text: str):
        self.call('incoming', **{
            'message': text,
            'is_my': 0,
            'is_system': 1,
            'image': '/img/logo.svg',
            'name': 'System',
            'date': self.time_now()
        })

    def user_message(self, user, text):
        for client in self._CLIENTS.values():
            client.call('incoming', **{
                'message': text,
                'is_my': int(user['rowid']) == int(client.rowid),
                'is_system': 0,
                'image': email2avatar(user['email']),
                'name': user['login'],
                'date': self.time_now()
            })

    def on_close(self):
        pass
        super().on_close()

    def open(self):
        super().open()
        pass
