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
class AttrDict(dict):
    """
    A simple ict subclass allowing attribute access.
    """
    def __init__(self, orig):
        dict.__init__(orig)

    def __getattr__(self, item):
        retval = self.__getitem__(item)
        if isinstance(retval, dict) and not isinstance(retval, AttrDict):
            return AttrDict(retval)
        return retval

    def __setattr__(self, key, value):
        return self.__setitem__(key, value)
