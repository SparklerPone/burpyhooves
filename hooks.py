# This file is part of BurpyHooves.
# 
# BurpyHooves is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# BurpyHooves is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the#  GNU General Public License
# along with BurpyHooves.  If not, see <http://www.gnu.org/licenses/>.
import sys
import logging
import traceback
import re

from collections import defaultdict


class Hook:
    def __init__(self, tag, callback):
        self.tag = tag.lower()
        self.callback = callback
        self.id = id(self)

class HookManager:
    def __init__(self, bot):
        self.bot = bot
        self.hooks = defaultdict(list)
        self.waiting_hooks = defaultdict(list)
        self.waiting_to_unhook = []

    def add_hook(self, hook):
        self.waiting_hooks[hook.tag].append(hook)
        return hook.id

    def force_add_hook(self, hook):
        the_id = self.add_hook(hook)
        self._add_hooks()
        return the_id

    def _add_hooks(self):
        for event, callbackList in self.waiting_hooks.iteritems():
            self.hooks[event].extend(callbackList)

        self.waiting_hooks = defaultdict(list)

    def remove_hook(self, the_id):
        self.waiting_to_unhook.append(the_id)

    def force_remove_hook(self, the_id):
        self.remove_hook(the_id)
        self._remove_hooks()

    def _remove_hooks(self):
        for _, hooks in self.hooks.iteritems():
            remove = []
            for hook in hooks:
                if hook.id in self.waiting_to_unhook:
                    self.waiting_to_unhook.remove(hook.id)
                    remove.append(hook)

            for rem in remove:
                if rem in hooks:
                    hooks.remove(rem)

        self.waiting_to_unhook = []

    def run_hooks(self, event, event_args):
        event = event.lower()
        if event in self.hooks:
            for hook in self.hooks[event]:
                try:
                    hook.callback(self.bot, event_args)
                except Exception as e:
                    logging.error("Error running hooks for event %s!" % event, exc_info=sys.exc_info())
                    #traceback.print_exc()

        self._remove_hooks()
        self._add_hooks()

    def run_irc_hooks(self, ln, bot):
        self.run_hooks("irc_raw_%s" % ln.command, ln)
        self.run_hooks("irc_raw", ln)
        if ln.command == "PRIVMSG":
            message = ln.params[-1]
            if not message:
                return
            sender = ln.hostmask.nick
            for skynick in bot.skybot:
                if ln.hostmask.nick.lower() == skynick.lower():
                    message = re.sub(r"<[^>]*>\s*","",message)
                    break
            splitmsg = message.split(" ")
            for prefix in self.bot.config["misc"]["command_prefix"]:
                if splitmsg[0].decode('utf-8').startswith(prefix.decode('utf-8')):
                    command = splitmsg[0][1:]
                    args = splitmsg[1:]
                    event_args = {
                        "ln": ln,
                        "command": command,
                        "args": args,
                        "sender": sender,
                        "target": ln.params[0]
                    }
                    self.run_hooks("command_%s" % command.lower(), event_args)
