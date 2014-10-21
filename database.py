import sqlite3


class Database:
    def __init__(self, file):
        self.file = file
        self.handle = None

    def connect(self):
        self.handle = sqlite3.connect(self.file)
        self.handle.row_factory = sqlite3.Row  # Named column access instead of index.

    def execute(self, sql, args=None):
        """
        Execute an SQL statement which affects the database in some way.
        @param sql: The raw SQL statement to execute. Every '?' character in this will be replaced with an element of
                    args.
        @param args: The arguments to the SQL statement.
        """
        if args is None:
            args = []

        self.handle.cursor().execute(sql, args)
        self.handle.commit()

    def execute_returnable(self, sql, args=None):
        """
        Execute an SQL statement which returns rows.
        @param sql: The raw SQL statement to execute. Every '?' character in this will be replaced with an element of
                    args.
        @param args: The arguments to the SQL statement.
        @return: Database driver specific (currently SQLite3) list of Row objects.
        """
        if args is None:
            args = []

        return self.handle.cursor().execute(sql, args)
