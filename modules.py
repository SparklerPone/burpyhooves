import sys

class ModuleManager:
	def __init__(self, bot):
		self.bot = bot
		self.modules = {}

	def _get_info(self, module):
		name = "Unknown"
		description = "Unknown"

		if hasattr(module, "name"):
			name = module.name
		if hasattr(module, "description"):
			description = module.description

		return (name, description)

	def load_module(self, name):
		old_path = list(sys.path)
		sys.path[:] = ["./modules"]
		try:
			imported = __import__(name)
			loaded_module = getattr(imported, [x for x in dir(imported) if "__" not in x and "Module" in x][0])()
			setattr(loaded_module, "bot", self)
			self.modules[name] = loaded_module
			if hasattr(loaded_module, "module_init"):
				loaded_module.module_init(self.bot)
		except Exception as e:
			sys.path[:] = old_path
			return "Error loading module: %s" % str(e)

		sys.path[:] = old_path
		print("Loaded module: %s (%s)" % self._get_info(loaded_module))

	def unload_module(self, name):
		if name in self.modules:
			module = self.modules[name]
			if hasattr(module, "module_deinit"):
				module.module_deinit(self.bot)
			del self.modules[module]
