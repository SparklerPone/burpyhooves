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
from modules import Module

class CTCPModule(Module):
    def module_init(self, bot):
        self.hook_numeric("PRIVMSG", self.on_privmsg)

    def on_privmsg(self, bot, ln):
	message = ln.params[-1]
	if not message.startswith("\x01"):
	    return
        splitmsg = message.split(" ")
	ctcp = splitmsg[0][1:]
	if ctcp.endswith("\x01"):
	    ctcp = ctcp[:-1]
	for command in bot.config["ctcp"]["commands"]:
	    if command == ctcp:
		target = ln.hostmask.nick
		response = bot.config["ctcp"]["commands"][command]
		response = response.replace("%s"," ".join(splitmsg[1:]))
		bot.notice(target, "\x01" + command + " " + response + "\x01")

