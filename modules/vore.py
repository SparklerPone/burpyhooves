from hooks import CommandHook

class VoreModule:
	name = "Vore"
	description = "#vore-specific commands and chat responses."

	def module_init(self, bot):
		if "vore" not in bot.config:
			return "Vore section in config is required."

		self.config = bot.config["vore"]
		self.reacts = self.config["react_messages"]
		self.cmd_replies = self.config["command_replies"]
		