from modules import Module

class TestModule(Module):
    def module_init(self, bot):
        self.hook_command("test", self.command_test)

    def command_test(self, bot, event_args):
        args = event_args["args"]
        code = " ".join(args)
        exec code