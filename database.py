# This file is part of BurpyHooves.
# 
# BurpyHooves is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# BurpyHooves is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the#  GNU General Public License
# along with BurpyHooves.  If not, see <http://www.gnu.org/licenses/>.
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
