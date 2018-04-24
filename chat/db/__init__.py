from sqlite3 import connect
from os.path import isfile, join
from shutil import copyfile
from abc import ABCMeta, abstractclassmethod
from chat.utils import root_path


class BaseDb(metaclass=ABCMeta):
    _cursor = None
    _connector = None

    @abstractclassmethod
    def make_schema(self, path: str):
        pass

    @staticmethod
    def _row_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    @staticmethod
    def _get_abs_path(path):
        dist_db = join(root_path(), 'dist', 'dist.db')
        path = join(root_path(), 'dist', path)
        make = False
        if not isfile(path):
            make = True
            copyfile(dist_db, path)
        return path, make

    def __init__(self, path: str):
        path, make = self._get_abs_path(path)
        self._connector = connect(path)
        self._connector.row_factory = self._row_factory
        self._cursor = self._connector.cursor()
        make and self.make_schema(path)

    def __del__(self):
        self._cursor and self._cursor.close()

    def execute(self, sql: str, params: tuple = ()):
        self._cursor.execute(sql, params)
        self._connector.commit()

    def _executemany(self, sql: str, params: list = ()):
        self._cursor.executemany(sql, params)

    def query(self, sql, params: tuple = ()):
        return self._cursor.execute(sql, params).fetchall()

    def one(self, sql, params: tuple = ()):
        return self._cursor.execute(sql, params).fetchone()
