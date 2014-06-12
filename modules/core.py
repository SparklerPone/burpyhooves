from hooks import EventHook, CommandHook

class CoreModule:
	name = "Core"
	description = "Provides core management unctionality for the bot."

	def module_init(self, bot):
		bot.hook_manager.add_hook(CommandHook("modload", self.on_command_modload))

	def on_command_modload(self, bot, ln, args):
		if len(args) != 1:
			bot.reply("Usage: MODLOAD <module name>")
			return

		to_load = args[0]
		result = bot.module_manager.load_module(to_load)
		if result:
			bot.reply(result)
		else:
			bot.reply("Sucessfully loaded module %s!" % to_load)