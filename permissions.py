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
import json

from fnmatch import fnmatch

class Permissions:
    def __init__(self, bot):
        self.bot = bot
        self.permissions = json.load(open("etc/permissions.json"))["permissions"]

    def check_permission(self, hostmask, permission="admin"):
        """
        Check a permission on a hostmask, according to the loaded permissions file.
        Standard wildcards (* and ?) are supported because we use the fnmatch module here.

        @param hostmask: The hostmask to check the permission on.
        @param permission: The permission to check.
        @return: True if the hostmask has the permission, False otherwise.
        """
        for k in self.permissions:
            user = self.permissions[k]
            matched_nick = False
            matched_ident = False
            matched_host = False
            for nick in user["nicks"]:
                if fnmatch(hostmask.nick, nick):
                    matched_nick = True
                    break

            for ident in user["idents"]:
                if fnmatch(hostmask.user, ident):
                    matched_ident = True
                    break

            for host in user["hostnames"]:
                if fnmatch(hostmask.host, host):
                    matched_host = True
                    break

            if matched_nick and matched_ident and matched_host:
                return True

        return False  # Nothing matched fully.

    def rehash(self):
        self.permissions = json.load(open("permissions.json"))