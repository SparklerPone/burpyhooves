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

class RawModule(Module):
    def module_init(self, bot):
        self.hook_command("raw", self.command_raw)

    def command_raw(self, bot, event_args):
        if not bot.check_permission("admin", ""):
            bot.reply("Permission denied: You are not an admin.")
            return
        bot.raw(" ".join(event_args["args"]))

