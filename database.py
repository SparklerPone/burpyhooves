import sqlite3


class Database:
    def __init__(self, file):
        self.file = file
        self.handle = None

    def connect(self):
        self.handle = sqlite3.connect(self.file)
        self.handle.row_factory = sqlite3.Row  # Named column access instead of index.

    def execute(self, sql, args=None):
        if args is None:
            args = []

        self.handle.cursor().execute(sql, args)
        self.handle.commit()

    def execute_returnable(self, sql, args=None):
        if args is None:
            args = []

        return self.handle.cursor().execute(sql, args)
