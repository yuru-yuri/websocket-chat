
from tornado.web import RequestHandler


class Http(RequestHandler):
    def data_received(self, chunk):
        pass

    def post(self, *args, **kwargs):
        pass

    def _sign_in(self, **kwargs):
        pass

    def _sign_out(self):
        pass

    def _sign_up(self):
        pass
