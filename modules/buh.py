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
import random

class BuhModule(Module):
    def module_init(self, bot):
	random.seed()
        self.hook_command("bored", self.command_bored)

    def command_bored(self, bot, event_args):
	u = random.randint(1,20)
	colors = [random.randint(1,15) for i in xrange(2)]
	uColors = [random.randint(1,15) for i in xrange(random.randint(1,20))]
	msg = '\x03' + str(colors[0]) + 'b'
	for i in uColors:
	    msg += '\x03' + str(i) + 'u'
	msg += '\x03' + str(i) + 'h'
	bot.reply(msg)
