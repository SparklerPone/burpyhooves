from hooks import EventHook, CommandHook

class CoreModule:
	name = "Core"
	description = "Provides core management unctionality for the bot."

	def module_init(self, bot):
		self.hooks = []
		self.hooks.append(bot.hook_command("modload", self.on_command_modload))
		self.hooks.append(bot.hook_command("modunload", self.on_command_modunload))
		self.hooks.append(bot.hook_command("modreload", self.on_command_modreload))

	def module_deinit(self, bot):
		for hook in self.hooks:
			bot.unhook_something(hook)

	def on_command_modload(self, bot, ln, args):
		if not bot.check_permission():
			return

		if not bot.check_condition(len(args) == 1, "Usage: MODLOAD <module name>"):
			return

		to_load = args[0]
		result = bot.module_manager.load_module(to_load)
		if result:
			bot.reply(result)
		else:
			bot.reply("Sucessfully loaded module %s!" % to_load)

	def on_command_modunload(self, bot, ln, args):
		if not bot.check_permission():
			return

		if not bot.check_condition(len(args) == 1, "Usage: MODUNLOAD <module name>"):
			return

		to_unload = args[0]
		result = bot.module_manager.unload_module(to_unload)
		if result:
			bot.reply(result)
		else:
			bot.reply("Sucessfully unloaded module %s!" % to_unload)

	def on_command_modreload(self, bot, ln, args):
		if not bot.check_permission():
			return

		if not bot.check_condition(len(args) == 1, "Usage: MODRELOAD <module name>"):
			return

		to_reload = args[0]
		result = bot.module_manager.unload_module(to_reload, True)
		if result:
			bot.reply(result)
			return

		result = bot.module_manager.load_module(to_reload)
		if result:
			bot.reply(result)
		else:
			bot.reply("Sucessfully reloaded module: %s!" % to_reload)