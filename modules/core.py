from hooks import EventHook, CommandHook

class CoreModule:
	name = "Core"
	description = "Provides core management unctionality for the bot."

	def module_init(self, bot):
		bot.hook_manager.add_hook(CommandHook("modload", self.on_command_modload))

	def on_command_modload(self, bot, ln, args):
		pass # Do things...