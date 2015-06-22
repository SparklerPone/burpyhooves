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
class LineBuffer:
    def __init__(self, data=""):
        self.data = data

    def append(self, data):
        self.data += data

    def has_line(self):
        return "\n" in self.data

    def pop_line(self):
        if not self.has_line():
            return None

        lines = self.data.split("\n")
        line = lines.pop(0)
        self.data = "\n".join(lines)
        return line.strip()

    def flush(self):
        temp = self.data
        self.data = ""
        return temp

    def __iter__(self):
        return self

    def next(self):
        if self.has_line():
            return self.pop_line()

        raise StopIteration