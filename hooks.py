class EventHook:
	def __init__(self, event, callback):
		self.event = event
		self.callback = callback

class CommandHook:
	def __init__(self, command, callback):
		self.command = command
		self.callback = callback

class HookManager:
	def __init__(self, bot):
		self.bot = bot
		self.event_hooks = []
		self.cmd_hooks = []

	def add_hook(self, hook):
		if isinstance(hook, EventHook):
			self.event_hooks.append(hook)
		else:
			self.cmd_hooks.append(hook)

	def run_hooks(self, ln):
		for hook in self.event_hooks:
			if hook.event.lower() == ln.command.lower():
				hook.callback(self.bot, ln)

		if ln.command == "PRIVMSG":
			message = ln.params[-1]
			splitmsg = message.split(" ")
			if message[0] == self.bot.config["misc"]["command_prefix"]:
				command = splitmsg[0][1:]
				args = splitmsg[1:]
				for hook in self.cmd_hooks:
					if hook.command.lower() == command.lower():
						hook.callback(self.bot, ln, args)
