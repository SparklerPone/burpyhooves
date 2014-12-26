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