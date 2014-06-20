import re
import random

from hooks import CommandHook

class VoreModule:
	name = "Vore"
	description = "#vore-specific commands and chat responses."

	# These regexes are borrowed from GyroTech's code
	self_regex = "(?i)(((it|him|her|their|them)sel(f|ves))|Burpy\s?Hooves)"
	all_regex = "(?i)every\s?(body|one|pony|pone|poni)"

	def module_init(self, bot):
		if "vore" not in bot.config:
			return "Vore section in config is required."

		self.config = bot.config["vore"]
		self.reacts = self.config["react_messages"]
		self.cmd_replies = self.config["command_replies"]

		self.hooks = []
		self.hooks.append(bot.hook_command("eat", self.on_command_eat))

	def on_command_eat(self, bot, ln, args):
		me = bot.me["nicks"][0] # Temp hack!

		eaten = ln.hostmask.nick
		if len(args) > 0:
			eaten = " ".join(args)
		eaten = eaten.strip()

		reply = None

		if re.match(self.self_regex, eaten, re.IGNORECASE): # !eat BurpyHooves
			reply = random.choice(self.cmd_replies["eat_self"])
		elif re.match(self.all_regex, eaten, re.IGNORECASE): # !eat everypony
			reply = random.choice(self.cmd_replies["eat_all"])
		else:
			reply = random.choice(self.cmd_replies["eat_user"]) # !eat AppleDash (Or any other user.)

		bot.reply_act(reply % eaten)