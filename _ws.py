#!/usr/bin/env /usr/bin/python3
# -*- coding: utf-8 -*-

import os
import tornado.web
import tornado.httpserver
import tornado.ioloop
import time
import logging
from wsrpc import WebSocketRoute, WebSocket
from tornado.web import (RequestHandler, HTTPError)
import sys
import sqlite3
import json
import hashlib

allowFork = False
project_root = os.getcwd()
options = {
    'port': 9088,
    'listen': '127.0.0.1'
}
log = logging.getLogger('wsrpc.handler')

users_connection = sqlite3.connect('dist/users.db')
users_cursor = users_connection.cursor()
users_cursor.execute("""
    CREATE TABLE sqlite_sequence(name,seq);
    CREATE TABLE "users" (
        `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
        `login`	TEXT,
        `pass`	TEXT,
        `email`	TEXT,
        `token`	TEXT DEFAULT "",
        `date`	datetime,
        `online`	INTEGER DEFAULT 0
    );
""")
# c.execute('DROP TABLE users')
users_connection.commit()
messages_connection = sqlite3.connect('dist/msg.db')
messages_cursor = messages_connection.cursor()
# m.execute('DROP TABLE messages')
messages_cursor.execute("""
    CREATE TABLE sqlite_sequence(name,seq);
    CREATE TABLE "messages" (
        `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
        `user`	INTEGER,
        `message`	TEXT,
        `on_message`	INTEGER,
        `date`	datetime
    );
""")
messages_connection.commit()

messagesLimit = 100


def str2pass(_s: str):
    _h = hashlib.sha256()
    _h.update(_s.encode('utf-8'))
    return _h.hexdigest()


def email2img(_s: str):
    _h = hashlib.md5()
    _h.update(_s.encode('utf-8'))
    return _h.hexdigest()


def time_now():
    return time.strftime('%Y-%m-%d %H:%M:%S')


def login(_login: str, _password: str):
    """
    :param _login:
    :param _password:
    :return: dict
    """
    if len(_login) and len(_password):
        _password = str2pass(_password)
        result = users_cursor.execute(
            'SELECT ROWID, login, email FROM users WHERE lower(login) = lower(?) AND pass = ?',
            (_login, _password,)
        ).fetchone()
        if result is not None:
            return result
    return 0, '', '',


def signup(_login: str, _password: str, _email: str):
    """
    :param _login:
    :param _password:
    :param _email:
    :return: int
    """
    if len(_login) and len(_password) and len(_email) and _login != 'System' and _login != 'Admin':
        _password = str2pass(_password)
        result = users_cursor.execute(
            'SELECT ROWID FROM users WHERE lower(login) = lower(?) OR lower(email) = lower(?)',
            (_login, _email)
        ).fetchone()
        if result is None:
            users_cursor.execute(
                'INSERT INTO users (login, pass, email, token, date) VALUES (?, ?, ?, ?, ?)',
                (_login, _password, _email, '', time_now())
            )
            users_connection.commit()
            result = users_cursor.execute('SELECT last_insert_rowid()').fetchone()
            return 0 if result is None else result[0]
    return 0


def message(*args, **kwargs):
    user = args[0].get_secure_cookie('id')
    if not user:
        args[0].system_message('Please, login first!')
    else:
        _m = str(args[1]).strip()
        if len(_m) < 2 or len(_m) > 512:
            args[0].system_message('Length limitation from 2 to 512 characters')
            return None
        _m = _m.replace('<', '&lt;').replace('>', '&gt;')
        messages_cursor.execute('INSERT INTO messages (user, message, date) VALUES (?, ?, ?)',
                                (user, _m, time_now()))
        messages_connection.commit()
        _list = MyWebSocket._CLIENTS
        email = users_cursor.execute('SELECT email,login FROM users WHERE ROWID = ?',
                                     (user.decode('utf-8'), )).fetchone()
        md5 = 'default'
        _l = 'Anonymous'
        if email is not None:
            md5 = email2img(email[0])
            _l = email[1]
        for u in _list:
            _list[u].call('incoming', **{
                'message': _m,
                'is_my': 1 if args[0].id == u else 0,
                'is_system': 0,
                'image': '//gravatar.com/avatar/{}?s=96'.format(md5, ),
                'name': _l,
                'date': time_now()
            })


class User(RequestHandler):

    def _json(self, data: dict = ()):
        self.set_header('Content-type', 'application/json')
        if len(data):
            self.write(json.dumps(data))

    def _wrong_password(self):
        self._json({
            'result': False,
            'errors': [{
                'type': 'alert-warning',
                'text': 'Wrong login or password'
            }]
        })

    def post(self, *args, **kwargs):
        _d = json.loads(self.request.body.decode('utf-8'))
        _a = _d.keys()

        action = args[0].strip('/')
        if action == 'signin':
            if not ('login' in _a and 'password' in _a):
                self._json({
                    'result': False,
                    'errors': [{
                        'type': 'alert-warning',
                        'text': 'missing required argument (login|password)'
                    }]
                })
                return
            _l = _d['login']
            _p = _d['password']
            if _l == '' or _p == '':
                self._wrong_password()
                return
            result = login(_l, _p)
            if result[0] > 0:
                self.set_secure_cookie(name='id', value=str(result[0]))
            result = result[0] > 0
            self._json({
                'result': result,
                'errors': [] if result else [{
                    'type': 'alert-warning',
                    'text': 'Wrong login or password'
                }]
            })
        elif action == 'signup':
            if not ('login' in _a and 'password' in _a and 'email' in _a):
                self._json({
                    'result': False,
                    'errors': [{
                        'type': 'alert-warning',
                        'text': 'missing required argument (login|password|email)'
                    }]
                })
                return
            _l = _d['login']
            _p = _d['password']
            _e = _d['email']
            if _l == '' or _p == '' or _e == '':
                self._wrong_password()
                return
            result = signup(_l, _p, _e)
            if result > 0:
                self.set_secure_cookie(name='id', value=str(result))
            result = (result > 0)
            self._json({
                'result': result,
                'errors': [] if result else [{
                    'type': 'alert-warning',
                    'text': 'Busy login or email'
                }]
            })

        elif action == 'logout':
            self.set_secure_cookie(name='id', value='', expires_days=-1)
            self._json({
                'result': True
            })
        elif action == 'check':
            result = self.get_secure_cookie('id')
            if result is None:
                result = 0
            else:
                result = result.decode('utf-8')
            str_result = len(str(int(result)))
            result = True if result and (str_result == len(str(result))) else False
            users = []
            if True:
                u = users_cursor.execute('SELECT login, email, online FROM users WHERE online = 1').fetchall()
                for i in u:
                    _image = 'default'
                    if len(i[1]):
                        _image = email2img(i[1])
                    _ = {'login': i[0], 'image': '//gravatar.com/avatar/{}?s=24'.format(_image, )}
                    users.append(_)
            self._json({
                'result': result,
                'users': users
            })
        elif action == 'messages':
            if 'time' in _a and 'h' in _d['time'].keys() and 'm' in _d['time'].keys():
                _t = "{} {}:{}:00".format(time.strftime('%Y-%m-%d '), _d['time']['h'], _d['time']['m'])
                _m = messages_cursor.execute(
                    'SELECT message, date, user FROM messages WHERE date < ? ORDER BY ROWID DESC', (_t,)
                ).fetchmany(100)
            else:
                _m = messages_cursor.execute(
                    'SELECT message, date, user FROM messages ORDER BY ROWID DESC'
                ).fetchmany(30)
                if _m is None:
                    _m = []
                _m.reverse()
            items = []
            _keys = []
            md5 = 'default'
            _l = 'Anonymous'
            sid = self.get_secure_cookie('id')
            if sid is None:
                sid = 0
            else:
                sid = sid.decode('utf-8')
            emails = {}
            if _m is not None:
                _e = users_cursor.execute('SELECT ROWID, email, login FROM users').fetchall()
                emails = {inner_e[0]: [inner_e[1], inner_e[2]] for inner_e in _e}
                _keys = emails.keys()
            for i in _m:
                if int(i[2]) in _keys:
                    _ = emails[int(i[2])]
                    md5 = email2img(_[0])
                    _l = _[1]
                items.append({
                    'message': i[0],
                    'date': i[1],
                    'is_my': 1 if int(sid) == int(i[2]) else 0,
                    'is_system': 0,
                    'image': '//gravatar.com/avatar/{}?s=96'.format(md5, ),
                    'name': _l
                })
            self._json({
                'result': True,
                'items': items
            })
        else:
            raise HTTPError(403)


MyWebSocket.ROUTES['message'] = message
MyWebSocket.ROUTES['getTime'] = lambda t: time.time()

if __name__ == "__main__":

    print('Starting server: %s:%d' % (options['listen'], int(options['port'])), file=sys.stdout)

    if allowFork:
        try:
            pid = os.fork()
            if pid:
                print('Daemon started with pid %d' % pid)
                sys.exit(0)
        except Exception as e:
            print('Could not daemonize, script will run in foreground. Error was: "%s"' % str(e), file=sys.stderr)

    _f = open('dist/secret.txt', 'rb')
    secret = _f.read(2048)
    _f.close()

    http_server = tornado.httpserver.HTTPServer(tornado.web.Application((
        (r"/ws/", MyWebSocket),
        (r"/user/(\w+(/?))", User),
        (r'/(.*)', tornado.web.StaticFileHandler, {
            'path': os.path.join(project_root, 'static'),
            'default_filename': 'index.html'
        }),
    ), cookie_secret=secret))

    http_server.listen(options['port'], address=options['listen'])
    tornado.ioloop.IOLoop.instance().start()
