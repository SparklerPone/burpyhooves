import sys
import logging
import traceback

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
        """
        Load a module into the bot.
        @param name: The name of the module, without trailing file extension.
        @return: Status or error message. (TODO: Set a flag instead and return True or False for success/failure)
        """
        if name in self.modules:
            logging.error("Module already loaded.")
            return "Error: Module already loaded."

        old_path = list(sys.path)
        sys.path.insert(0, "./modules")
        try:
            imported = __import__(name)
            loaded_module = getattr(imported, [x for x in dir(imported) if "__" not in x and "Module" in x and len(x) > len("Module")][0])()
            if not isinstance(loaded_module, Module):
                sys.path[:] = old_path
                logging.error("Error loading module '%s': Not a Module (forgetting something?)" % name)
                return "Error loading module '%s': Not a Module (forgetting something?)" % name

            setattr(loaded_module, "bot", self.bot)
            loaded_module._module_init(self.bot)
            if hasattr(loaded_module, "module_init"):
                result = loaded_module.module_init(self.bot)
                if result:
                    sys.path[:] = old_path
                    logging.error("Error loading module '%s': %s" % (name, result))
                    return "Error loading module '%s': %s" % (name, result)

            self.modules[name] = loaded_module
        except Exception as e:
            sys.path[:] = old_path
            x = "Error loading module: '%s': %s" % (name, str(e))
            #traceback.print_exc()
            logging.exception(x, exc_info=sys.exc_info())
            return x

        sys.path[:] = old_path
        logging.info("Loaded module: %s (%s)" % self._get_info(loaded_module))
        return "Loaded module: %s (%s)" % self._get_info(loaded_module)

    def unload_module(self, name, bypass_core=False):
        """
        Unload a module.
        @param name: Name of a loaded module.
        @param bypass_core: True if name is allowed to be "core", else False.
        @return: Status or error message. (TODO: Set a flag instead and return True or False for success/failure)
        """
        if name == "core" and not bypass_core:
            logging.error("Error: Cannot unload the core module!")
            return "Error: Cannot unload the core module!"

        if name in self.modules:
            module = self.modules[name]
            module._module_deinit(self.bot)
            if hasattr(module, "module_deinit"):
                module.module_deinit(self.bot)
            del self.modules[name]
            del sys.modules[name]
        else:
            logging.error("Error: Module not loaded")
            return "Error: Module nod loaded."

        logging.info("Unloaded module: %s (%s)" % self._get_info(module))
        return "Unloaded module: %s (%s)" % self._get_info(module)


class Module:
    def _module_init(self, bot):
        self.hooks = []

    def _module_deinit(self, bot):
        for hook in self.hooks:
            bot.unhook_something(hook)

    def hook_command(self, command, callback):
        """
        Hook a command in the bot.
        See BurpyHooves.hook_command()
        """
        hook = self.bot.hook_command(command, callback)
        self.hooks.append(hook)

    def hook_numeric(self, event, callback):
        """
        Hook a raw IRC numeric in the bot.
        See BurpyHooves.hook_numeric()
        """
        hook = self.bot.hook_numeric(event, callback)
        self.hooks.append(hook)
