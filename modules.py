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
        if name in self.modules:
            return "Error: Module already loaded."
        old_path = list(sys.path)
        sys.path.insert(0, "./modules")
        try:
            imported = __import__(name)
            loaded_module = getattr(imported, [x for x in dir(imported) if "__" not in x and "Module" in x and len(x) > len("Module")][0])()
            if not isinstance(loaded_module, Module):
                sys.path[:] = old_path
                return "Error loading module '%s': Not a Module (forgetting something?)" % name

            setattr(loaded_module, "bot", self.bot)
            self.modules[name] = loaded_module
            loaded_module._module_init(self.bot)
            if hasattr(loaded_module, "module_init"):
                result = loaded_module.module_init(self.bot)
                if result:
                    sys.path[:] = old_path
                    return "Error loading module '%s': %s" % (name, result)
        except Exception as e:
            sys.path[:] = old_path
            return "Error loading module: '%s': %s" % (name, str(e))

        sys.path[:] = old_path
        print("Loaded module: %s (%s)" % self._get_info(loaded_module))

    def unload_module(self, name, bypass_core=False):
        if name == "core" and not bypass_core:
            return "Error: Cannot unload the core module!"

        if name in self.modules:
            module = self.modules[name]
            module._module_deinit(self.bot)
            if hasattr(module, "module_deinit"):
                module.module_deinit(self.bot)
            del self.modules[name]
            del sys.modules[name]
        else:
            return "Error: Module not loaded"

        print("Unloaded module: %s (%s)" % self._get_info(module))


class Module:
    def _module_init(self, bot):
        self.hooks = []

    def _module_deinit(self, bot):
        for hook in self.hooks:
            bot.unhook_something(hook)

    def hook_command(self, command, callback):
        hook = self.bot.hook_command(command, callback)
        self.hooks.append(hook)

    def hook_event(self, event, callback):
        hook = self.bot.hook_event(event, callback)
        self.hooks.append(hook)
