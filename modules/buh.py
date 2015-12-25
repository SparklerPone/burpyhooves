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
        self.hook_command("boredx", self.command_boredx)

    def gen_buh(self,length):
        colors = [random.randint(1,15) for i in xrange(2)]
        uColors = [random.randint(1,15) for i in xrange(random.randint(1,length))]
        blast = True if random.randint(1,25) == 1 else False

        msg = '\x03' + str(colors[0])
        if blast:
            msg += 'h'
        else:
            msg += 'b'
        msg += self.gen_u(uColors)
        msg += '\x03' + str(random.randint(1,15))
        if blast:
            msg += 'b'
        else:
            msg += 'h'
        return msg

    def gen_u(self, colors):
        u = ""
        for i in colors:
            u += '\x03' + str(i) + 'u'
        return u

    def command_bored(self, bot, event_args):
	msg = self.gen_buh(random.randint(1,20))
	bot.reply(msg)

    def command_boredx(self, bot, event_args):
        msg = self.gen_buh(random.randint(1,50))
        bot.reply(msg)

