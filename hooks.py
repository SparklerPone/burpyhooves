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
		self.event_hooks = {}
		self.cmd_hooks = {}

		self.waiting_to_unhook = []
		self.waiting_event_hooks = []
		self.waiting_cmd_hooks = []

	def add_hook(self, hook):
		the_id = id(hook)
		if isinstance(hook, EventHook):
			self.waiting_event_hooks.append(hook)
		else:
			self.waiting_cmd_hooks.append(hook)

		return the_id

	def really_add_hook(self, hook):
		the_id = self.add_hook(hook)
		self._add_hooks()
		return the_id

	def _add_hooks(self):
		for hook in self.waiting_event_hooks:
			the_id = id(hook)
			self.event_hooks[the_id] = hook

		for hook in self.waiting_cmd_hooks:
			the_id = id(hook)
			self.cmd_hooks[the_id] = hook

		self.waiting_event_hooks = []
		self.waiting_cmd_hooks = []

	def remove_hook(self, the_id):
		self.waiting_to_unhook.append(the_id)

	def really_remove_hook(self, the_id):
		self.remove_hook(the_id)
		self._remove_hooks()
	
	def _remove_hooks(self):
		for the_id in self.waiting_to_unhook:
			if the_id in self.event_hooks:
				del self.event_hooks[the_id]

			if the_id in self.cmd_hooks:
				del self.cmd_hooks[the_id]

		self.waiting_to_unhook = []

	def run_hooks(self, ln):
		for hook_id in self.event_hooks:
			hook = self.event_hooks[hook_id]
			if hook.event.lower() == ln.command.lower():
				hook.callback(self.bot, ln)

		if ln.command == "PRIVMSG":
			message = ln.params[-1]
			splitmsg = message.split(" ")
			if message[0] == self.bot.config["misc"]["command_prefix"]:
				command = splitmsg[0][1:]
				args = splitmsg[1:]
				for hook_id in self.cmd_hooks:
					hook = self.cmd_hooks[hook_id]
					if hook.command.lower() == command.lower():
						hook.callback(self.bot, ln, args)

		self._remove_hooks()
		self._add_hooks()
