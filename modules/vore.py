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
import re
import random

from modules import Module


class VoreModule(Module):
    name = "Vore"
    description = "#vore-specific commands and chat responses."

    # These regexes are borrowed from GyroTech's code
    self_regex = "(?i)(((it|him|her|their|them)sel(f|ves))|Burpy\s?Hooves)"
    all_regex = "(?i)every\s?(body|one|pony|pone|poni)"

    def module_init(self, bot):
        if "vore" not in bot.config:
            return "Vore section in config is required."

        self.config = bot.config["vore"]
        self.reacts = self.config["react_messages"]
        self.cmd_replies = self.config["command_replies"]

        self.hook_command("eat", self.on_command_eat)
        self.hook_command("cockvore", self.on_command_cockvore)
        self.hook_command("inflate", self.on_command_inflate)

    def do_command_reply(self, bot, target, replies):
        # Replies is a 3-tuple of lists that looks like: (replies for target=me, replies for target=all, replies for target=user)
        reply = None
        if re.match(self.self_regex, target, re.IGNORECASE):  # !eat BurpyHooves
            reply = random.choice(replies[0])
        elif re.match(self.all_regex, target, re.IGNORECASE):  # !eat everypony
            reply = random.choice(replies[1])
        else:
            reply = random.choice(replies[2])  # !eat AppleDash (Or any other user.)

        try:
            bot.reply_act(reply % target)
        except TypeError:  # Format string wasn't filled. (No %s)
            bot.reply_act(reply)

    def on_command_eat(self, bot, ln, args):
        eaten = ln.hostmask.nick
        if len(args) > 0:
            eaten = " ".join(args)
        eaten = eaten.strip()

        self.do_command_reply(bot, eaten, (self.cmd_replies["eat_self"], self.cmd_replies["eat_all"], self.cmd_replies["eat_user"]))

    def on_command_cockvore(self, bot, ln, args):
        cockvored = ln.hostmask.nick
        if len(args) > 0:
            cockvored = " ".join(args)
        cockvored = cockvored.strip()

        self.do_command_reply(bot, cockvored, (self.cmd_replies["cockvore_self"], self.cmd_replies["cockvore_all"], self.cmd_replies["cockvore_user"]))

    def on_command_inflate(self, bot, ln, args):
        inflated = ln.hostmask.nick
        if len(args) > 0:
            inflated = " ".join(args)
        inflated = inflated.strip()
        if re.match(self.all_regex, inflated, re.IGNORECASE):  # Not implemented
            return

        self.do_command_reply(bot, inflated, (self.cmd_replies["inflate_self"], [], self.cmd_replies["inflate_user"]))

