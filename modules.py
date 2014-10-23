import sys
import logging
import traceback

class ModuleException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "ModuleException(%s)" % self.message

class ModuleManager:
    def __init__(self, bot):
        self.bot = bot
        self.modules = {}
        self.last_error = None

    def on_error(self, message):
        logging.error(message)
        self.last_error = message

    def raise_for_error(self):
        if self.last_error:
            err = self.last_error
            self.last_error = None
            raise ModuleException(err)

    def load_module(self, name):
        """
        Load a module into the bot.
        @param name: The name of the module, without trailing file extension.
        @return: Status or error message. (TODO: Set a flag instead and return True or False for success/failure)
        """
        if name in self.modules:
            self.on_error("Module already loaded!")
            return False

        old_path = list(sys.path)
        sys.path.insert(0, "./modules")
        try:
            imported = __import__(name)
            loaded_module = getattr(imported, [x for x in dir(imported) if "__" not in x and "Module" in x and len(x) > len("Module")][0])()
            if not isinstance(loaded_module, Module):
                sys.path[:] = old_path
                self.on_error("Error loading module '%s': Not a Module (forgetting something?)" % name)
                return False

            setattr(loaded_module, "bot", self.bot)
            loaded_module._module_init(self.bot)
            if hasattr(loaded_module, "module_init"):
                result = loaded_module.module_init(self.bot)
                if result:
                    sys.path[:] = old_path
                    self.on_error("Error loading module '%s': %s" % (name, result))
                    return False

            self.modules[name] = loaded_module
        except Exception as e:
            sys.path[:] = old_path
            x = "Error loading module: '%s': %s" % (name, str(e))
            logging.exception(x, exc_info=sys.exc_info())
            self.on_error(x)
            return False

        sys.path[:] = old_path
        logging.info("Loaded module: %s" % str(loaded_module))
        return True

    def unload_module(self, name, bypass_core=False):
        """
        Unload a module.
        @param name: Name of a loaded module.
        @param bypass_core: True if name is allowed to be "core", else False.
        @return: Status or error message. (TODO: Set a flag instead and return True or False for success/failure)
        """
        if name == "core" and not bypass_core:
            self.on_error("Error: Cannot unload the core module!")
            return False

        if name in self.modules:
            module = self.modules[name]
            module._module_deinit(self.bot)
            if hasattr(module, "module_deinit"):
                module.module_deinit(self.bot)
            del self.modules[name]
            del sys.modules[name]
        else:
            self.on_error("Error: Module not loaded")
            return False

        logging.info("Unloaded module: %s" % str(module))
        return True


class Module:
    name = "Unknown"
    description = "Unknown"

    def __init__(self):
        """
        Unused constructor to make IDEs happy.
        """
        self.bot = None

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

    def __str__(self):
        return "%s (%s)" % (self.name, self.description)