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
import datetime
import string

class RPLoggerModule(Module):
    name = "RPLogger"
    description = "RP Log Replay Module"
    chanlist = list()

    def module_init(self, bot):
	bot.db.execute("CREATE TABLE IF NOT EXISTS rplogger (id INTEGER PRIMARY KEY, name TEXT, players TEXT, timestart DATETIME DEFAULT CURRENT_TIMESTAMP, timeend DATETIME DEFAULT CURRENT_TIMESTAMP)")
	bot.db.execute("CREATE TABLE IF NOT EXISTS rp_lines (id INTEGER, nick TEXT, content TEXT, ooc BOOL, time DATETIME DEFAULT CURRENT_TIMESTAMP)")
	self.hook_numeric("PRIVMSG", self.on_privmsg)
	self.hook_command("rpstart", self.command_rpstart)
	self.hook_command("rpstop", self.command_rpstop)
	self.hook_command("rpadd", self.command_rpadd)
	self.hook_command("rplast", self.command_rplast)
	self.hook_command("rpraw", self.command_rpraw)
	self.hook_command("rphelp", self.command_rphelp)
	self.hook_command("rpsearch", self.command_rpsearch)
	self.hook_command("rpstatus", self.command_rpstatus)


    def on_privmsg(self, bot, ln):
	#do stuff... what AM I doing again?
	message = ln.params[-1]
	splitmsg = message.split(" ")
	args = splitmsg
	event_args = {
	"ln": ln,
	"args": args,
	"sender": ln.hostmask.nick,
	"target": ln.params[0]
	}
	
	#TODO: Timeout old RPs

	args = event_args["args"]
	if args and args[0][0] == bot.config["misc"]["command_prefix"]:
	    #bot command, handle elsewhere
	    return

	#check if active RP in channel
	chan = None
	for channel in self.chanlist:
	    if channel[1] == event_args["target"].lower():
		chan = channel[1]
		break
	if not chan:
	    #not a logged channel
	    return

	print "Active RP in channel"

	#check if nick is in RP
	log = False
	nick = event_args["sender"].lower()
	for rp in self.chanlist:
	    if rp[1] == event_args["target"].lower():
		names = self.get_rp_names(bot,rp[0])
		for name in names:
		    if nick == name.lower():
			log = True
			break
	if not log:
	    return

	#check for OOC
	OOC = False
	if event_args["args"][0] != "\x01ACTION":
	    OOC = True
	#add to DB
	print "Added to DB"
	finmessage = unicode(str.join(" ",args), errors='replace')
	bot.db.execute("INSERT INTO rp_lines (id, nick, content, ooc) VALUES (?, ? ,? ,?)", (self.get_rp_id(bot, rp[0]), event_args["sender"],finmessage,OOC))
	bot.db.execute("UPDATE rplogger SET timeend=CURRENT_TIMESTAMP WHERE id=(?)",(self.get_rp_id(bot, rp[0]),))

    def command_rphelp(self, bot, event_args):
	args = event_args["args"]
	if len(args) == 0:
	    bot.reply("rphelp: Possible commands: rpstart rpstop rpadd rplast rpraw rpsearch rpstatus rphelp: Nothing else is documented, good luck")

    def command_rpstart(self, bot, event_args):
	nick = event_args["sender"].lower()
	args = event_args["args"]
	channel = event_args["target"]
	if event_args["target"][0] != "#":
	    if len(args) < 2:
		bot.reply("You must specify a channel to start logging from query.")
		return
	    if args[1][0] != "#":
		bot.reply("You must specify the channel as the second parameter.")
		return
	    channel = args[1]
	if len(args) == 0:
	    bot.reply("You must specify a name.")
	    return
	if self.check_rp_exists(bot, args[0].lower()):
	    #check to be sure they were in that RP
	    if not self.check_char_in_rp(bot, args[0].lower(), nick):
		bot.reply("You are not in that RP, you cannot start it")
		return
	    bot.reply("RP %s resumed and now logging." % args[0])
	else:
	    #RP doesn't exist, create it
	    bot.db.execute("INSERT into rplogger (name, players) VALUES (?, ?)", (args[0], event_args["sender"]))
	    bot.reply("RP %s created and now logging." % args[0])

	self.chanlist.append((args[0], channel.lower()))
	

    def command_rpstop(self, bot, event_args):
	args = event_args["args"]
	if len(args) != 0:
	    name = event_args["args"][0].lower()
	else:
	    name = None
	nick = event_args["sender"]
	targetchannel = event_args["target"].lower()
	if targetchannel[0] == "#":
	    if name:
		for rp in self.chanlist:
		    if rp[1] == targetchannel:
			targetchannel = targetchannel
	    else:
		targetchannel = targetchannel
	if name:
	    if not self.check_rp_exists(bot, name):
        	bot.reply("RP %s does not exist." % name)
        	return

	    if not self.check_char_in_rp(bot, name, nick.lower()):
		bot.reply("You are not in this rp, you cannot stop it.")
		return

	    for rp in self.chanlist:
		if rp[0] == args[0]:
		    targetchannel = rp[1]
		    break
	
	    self.chanlist.remove((args[0], targetchannel))
	    bot.reply("Stopped logging of RP %s." % name)

    def command_rpadd(self, bot, event_args):
	args = event_args["args"]
	nick = event_args["sender"]
	if len(args) != 2:
	    bot.reply("rpadd requires exactly 2 parameters")
	    return
	name = args[0].lower()
	if not self.check_rp_exists(bot, name):
	    bot.reply("rp %s does not exist" % name)
	    return
	if not self.check_char_in_rp(bot, name, nick.lower()):
	    bot.reply("You are not in this rp, you cannot modify it")
	    return
	if not self.check_char_in_rp(bot, name, nick.lower()):
	    bot.reply("%s is already in this rp." % name)
	    return
	res = bot.db.execute_returnable("SELECT players FROM rplogger WHERE name=?", (name,))
	data = res.fetchall()
	players = str.join(" ", data[0])
	players += " " + args[1]
	bot.db.execute("UPDATE rplogger SET players = ? WHERE name=?", (players, name))
	bot.reply("Successfully added %s to the RP" % args[1])

    def command_rplast(self, bot, event_args):
	args = event_args["args"]
	if len(args) == 0:
	    bot.reply("You must provide an RP name")
	    return

	name = args[0].lower()
	if not self.check_rp_exists(bot, name):
	    bot.reply("RP %s does not exist" % name)
	    return

	ooc = False
	lines = 0
	if len(args) > 1:
	    if args[1] == "ooc":
		ooc = True
	    try:
		lines = int(args[1])
		if len(args) > 2:
		    if args[2] == "ooc":
			ooc = True
	    except ValueError:
		if len(args) > 2:
		    if args[1] == "ooc":
			ooc = True
		    try:
			lines = int(args[2])
		    except ValueError:
			pass
	res = None
	if ooc:
	    res = bot.db.execute_returnable("SELECT nick,content,time from rp_lines WHERE id=?", (self.get_rp_id(bot, name),))
	else:
	    res = bot.db.execute_returnable("SELECT nick,content,time from rp_lines WHERE id=? AND ooc='0'", (self.get_rp_id(bot, name),))
	data = res.fetchall()
	
	if not data:
	    bot.reply("Nothing found")
	    return
	data.reverse()
	messages = list()
	if self.check_char_in_rp(bot, name, event_args["sender"].lower()) and lines == 0:
	    #return all since last post
	    bot.reply("Replaying all lines since your last post.")
	    for line in data:
		if line[0] == event_args["sender"]:
		    break
		if line[1][0] == "\x01":
		    print line[1]
		    messages.append("*" + line[0] + line[1].strip("\x01")[6:])
		else:
		    messages.append(line[0] + ": " +line[1])
	else:
	    if lines == 0:
		lines = 3
	    lines -= 1
	    print data
	    poster = data[0][0]
	    bot.privmsg(event_args["sender"], "Replaying the last " + str(lines+1) + " line(s) in the RP")
	    for line in data:
		if line[1][0] == "\x01":
		    messages.append("*" + line[0] + str(line[1]).strip("\x01")[6:])
		else:
		    messages.append(line[0] + ": " +line[1])
		if line[0] == poster:
		    continue
		lines -= 1
		if lines <= 0:
		    break
		poster = line[0]

	messages.reverse()
	for message in messages:
	    bot.privmsg(event_args["sender"],message)

    def command_rpraw(self, bot, event_args):
	bot.reply("rpraw stub")

    def command_rpsearch(self, bot, event_args):
	bot.reply("rpsearch stub")

    def command_rpstatus(self, bot, event_args):
	args = event_args["args"]
	if len(args) < 1:
	    bot.reply("You must specify an RP or channel.")
	if args[0][0] == "#":
	    message = list()
	    for rp in self.chanlist:
		if rp[0] == args[0][0]:
		    message.append(rp[1])
	    bot.reply("The following RPs are active here: " + message.join(" "))
	else:
	    res = bot.db.execute_returnable("SELECT * FROM rplogger WHERE name=?", (args[0],))
	    data = res.fetchall()
	    if not data:
		bot.reply("No data found.")
		return
	    message = "ID: " + str(data[0][0]) + " Players: " + str(data[0][2]) + " Start Time: " + str(data[0][3]) + " Last Post Time: " + str(data[0][4])
	    for rp in self.chanlist:
		if rp[0] == args[0]:
		    message += " Currently active in " + rp[1]
	    bot.reply(message)
	    

    def check_rp_exists(self, bot, name):
	res = bot.db.execute_returnable("SELECT * FROM rplogger WHERE name=?", (name,))
	data = res.fetchall()
	return data != []

    def check_char_in_rp(self, bot, rpname, charname):
	res = bot.db.execute_returnable("SELECT players FROM rplogger WHERE name=?", (rpname,))
	data = res.fetchall()
	data = data[0][0]
	return charname in data.lower()

    def get_rp_names(self, bot, name):
	res = bot.db.execute_returnable("SELECT players FROM rplogger WHERE name=?", (name,))
	data = res.fetchall()
	datalist = str(data[0][0]).split(" ")
	return datalist

    def get_rp_id(self, bot, name):
	res = bot.db.execute_returnable("SELECT id FROM rplogger WHERE name=?", (name,))
	data = res.fetchall()
	return data[0][0]

    def check_rp_exists(self, bot, name):
	res = bot.db.execute_returnable("SELECT * FROM rplogger WHERE name=?", (name,))
	data = res.fetchall()
	return data != []
