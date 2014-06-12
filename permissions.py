import json

class Permissions:
	def __init__(self, bot):
		self.bot = bot
		self.permissions = json.load(open("permissions.json"))

	def check_permission(hostmask, permission="admin"):
		for user in self.permissions:
			matched_nick = False
			matched_ident = False
			matched_host = False
			for nick in user["nicks"]:
				if nick == hostmask.nick:
					matched_nick = True
					break

			for ident in user["idents"]:
				if ident == hostmask.user:
					matched_ident = True
					break

			for host in user["hostnames"]:
				if host == hostmask.host:
					matched_host = True
					break

			if matched_nick and matched_ident and matched_host:
				return True

		return False # Nothing matched fully.

	def rehash(self):
		self.permissions = json.load(open("permissions.json"))