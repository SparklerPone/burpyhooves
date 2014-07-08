import sqlite3

# This doesn't work yet
class Database:
    def __init__(self, file):
        self.file = file
        self.handle = None

    def connect(self):
        self.handle = sqlite3.connect(self.file)
        self.handle.row_factory = sqlite3.Row  # Named column access instead of index.

    def select(self, what, where, how=""):
        query = "SELECT %s FROM `%s` %s" % (what, where, how)
        result = self.handle.cursor().execute(query)
        return result

    def insert(self, where, data):
        columns = ", ".join(["`%s`" % n for n in data.keys()])
        values = " ".join("?" * len(data.values()))
        query = "INSERT INTO `%s` (%s) VALUES (%s)" % (where, columns, values)
        self.handle.cursor().execute(query)
        self.handle.commit()

    def delete(self, where, how):
        query = "DELETE FROM `%s` %s" % (where, how)
        self.handle.cursor().execute(query)
        self.handle.commit()

    def execute(self, sql):
        self.handle.cursor().execute(sql)
        self.handle.commit()

    def execute_returnable(self, sql):
        return self.handle.cursor().execute(sql)
