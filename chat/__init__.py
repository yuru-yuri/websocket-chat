from . import web_socket
from . import http
from .db.user import User
from .db.message import Message
from .utils import root_path
import os

import tornado.httpserver
import tornado.web
import tornado.ioloop


def main():
    # web_socket.make_route()  # TODO
    tornado.httpserver.HTTPServer(tornado.web.Application((
        (r'/ws/', web_socket.ChatWebSocket),
        (r'/user/(\w+)/?', http.Http),
        (r'/.*', tornado.web.StaticFileHandler, {
            'path': os.path.join(root_path(), 'static'),
            'default_filename': 'index.html'
        })
    )))
    # user = User()
    pass
