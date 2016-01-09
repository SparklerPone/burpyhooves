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
# You should have received a copy of the GNU General Public License
# along with BurpyHooves.  If not, see <http://www.gnu.org/licenses/>.

from modules import Module
from collections import deque
import string
import sqlite3
import datetime
import re
import random

class MuckModule(Module):
    name = "muck"
    description = "Character container"
    message_queue = deque()
    dbconn = 0
    attributes = [ "irc_name", "fullname", "othername", "sex", "species", "job", "age", "coat", "mane", "accessories", "eyes", "cm", "orientation",
		   "height", "weight", "smell", "taste", "feel", "fetish", "url", "short", "long1", "long2",
		   "long3"]
    sqlattributes = [ "char_ircname", "char_fullname", "char_othername", "char_sex", "char_species", "char_job", "char_age", "char_coat",
		      "char_mane", "char_accessories", "char_eyes", "char_cm", "char_orientation", "char_height",
		      "char_weight", "char_smell", "char_taste", "char_feel", "char_fetish", "char_url",
		      "char_short", "char_long1", "char_long2", "char_long3"]

    def module_init(self, bot):

	try:
	    self.dbconn = sqlite3.connect('etc/characters.db')
	    c = self.dbconn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS characters
             (char_name TEXT NOT NULL, char_sex TEXT, char_species TEXT, char_job TEXT,
              char_age INTEGER, char_coat TEXT, char_mane TEXT, char_eyes TEXT,
              char_cm TEXT, char_orientation TEXT, char_height TEXT, char_weight TEXT,
              char_smell TEXT, char_taste TEXT, char_feel TEXT, char_fetish TEXT,
              char_short TEXT, char_long1 TEXT, char_long2 TEXT, char_long3 TEXT,
              nickserv_account TEXT NOT NULL);''')
	    self.dbconn.commit()
	except Exception as e:
	    print("Failed to open sql database! %s" % (str(e)))
	    return "Could not open database, see console for more details. Aborting!"
	
	c.execute("PRAGMA user_version;")
	version = list(c.fetchone())
	if version[0] < 1:
	     try:
		print("Old version of DB detected, updating to version 1.")
		c.execute('''CREATE TABLE characters_new
         	(char_ircname TEXT NOT NULL, char_fullname TEXT, char_othername TEXT, char_sex TEXT, char_species TEXT, char_job TEXT,
         	 char_age INTEGER, char_coat TEXT, char_mane TEXT, char_accessories TEXT, char_eyes TEXT,
          	 char_cm TEXT, char_orientation TEXT, char_height TEXT, char_weight TEXT,
          	 char_smell TEXT, char_taste TEXT, char_feel TEXT, char_fetish TEXT, char_url TEXT, 
           	 char_short TEXT, char_long1 TEXT, char_long2 TEXT, char_long3 TEXT,
          	 nickserv_account TEXT NOT NULL, timestamp TEXT);''')
	 	c.execute("ALTER TABLE characters add column char_fullname TEXT")
	 	c.execute("ALTER TABLE characters add column char_othername TEXT")
	 	c.execute("ALTER TABLE characters add column char_accessories TEXT")
	 	c.execute("ALTER TABLE characters add column char_url TEXT")
	 	c.execute("ALTER TABLE characters add column timestamp TEXT")
		self.dbconn.commit()
		c.execute('''SELECT char_name,char_fullname,char_othername,char_sex,char_species,char_job,char_age,char_coat,
			char_mane,char_accessories,char_eyes,char_cm,char_orientation,char_height,char_weight,char_smell,
			char_taste,char_feel,char_fetish,char_url,char_short,char_long1,char_long2,char_long3,nickserv_account,
			timestamp FROM characters''')
	 	rows = c.fetchall()
		for row in rows:
		    c.execute("INSERT INTO characters_new VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", row)
		c.execute("DROP TABLE characters")
		c.execute("ALTER TABLE characters_new RENAME TO characters")
		c.execute("PRAGMA user_version = 1")
	 	self.dbconn.commit()
		version[0] = 1
	 	print("DB successfully updated to version 1!")
	     except Exception as e:
		print("Failed to update to version 1 DB, hopefully you had a backup. Aborting!")
		print("Exception was: %s" % (str(e)))
		return "Failed to update to DB version 1, see console for more details"

	if version[0] < 2:
	    try:
		print("Old version of DB detected, updating to version 2.")
		c.execute("ALTER TABLE characters add column creation_time")
		self.dbconn.commit()
		c.execute("PRAGMA user_version = 2")
		self.dbconn.commit()
		version[0] = 2
		print("DB successfully updated to version 2!")
            except Exception as e:
                print("Failed to update to version 2 DB, hopefully you had a backup. Aborting!")
                print("Exception was: %s" % (str(e)))
                return "Failed to update to DB version 2, see console for more details"
        if version[0] < 3:
            try:
                print("Old version of DB detected, updating to version 3.")
            except Exception as e:
                print("Failed to update to version 3 DB, hopefully you had a backup. Aborting!")
                print("Exception was: %s" % (str(e)))
                return "Failed to update to DB version 2, see console for more details"

	self.hook_command("claim", self.command_claim)
	self.hook_command("hoof", self.command_hoof)
	self.hook_command("help", self.command_help)
	self.hook_command("edit", self.command_edit)
	self.hook_command("delplayer", self.command_delplayer)
	self.hook_command("delchar", self.command_delchar)
	self.hook_command("listchars", self.command_listchars)
	self.hook_command("listallchars", self.command_listallchars)
	self.hook_command("dbversion", self.command_dbversion)
	self.hook_command("findchar", self.command_findchar)
	self.hook_command("techinfo", self.command_techinfo)
	self.hook_command("randomhorse", self.command_randomhorse)
	self.hook_numeric("330", self.handle_330)
	self.hook_numeric("PRIVMSG", self.on_privmsg)

    def on_privmsg(self, bot, ln):
	#TODO: Move to core
	message = ln.params[-1]
	splitmsg = message.split(" ")
	args = splitmsg[1:]
	command = ""
	if splitmsg[0][0:3].decode('utf8') == '\xe2\x98\x83'.decode('utf8'):
	    command = splitmsg[0][3:]
	event_args = {
        "ln": ln,
        "args": args,
        "sender": ln.hostmask.nick,
        "target": ln.params[0],
	"command": command
        }
	if command:
	    if command == "claim":
		self.command_claim(bot, event_args)
	    elif command == "hoof":
		self.command_hoof(bot, event_args)
	    elif command == "help":
		self.command_help(bot, event_args)
	    elif command == "edit":
		self.command_edit(bot, event_args)
	    elif command == "delplayer":
		self.command_delplayer(bot, event_args)
	    elif command == "delchar":
		self.command_delchar(bot, event_args)
	    elif command == "listchars":
		self.command_listchars(bot, event_args)
	    elif command == "listallchars":
		self.command_listallchars(bot, event_args)
	    elif command == "dbversion":
		self.command_dbversion(bot, event_args)
	    elif command == "findchar":
		self.command_findchar(bot, event_args)
	    elif command == "techinfo":
		self.command_techinfo(bot, event_args)

    def command_dbversion(self, bot, event_args):
	c = self.dbconn.cursor()
	c.execute("PRAGMA user_version;")
	row = c.fetchall()
	bot.reply(row[0][0])

    def command_help(self, bot, event_args):
	args = event_args["args"]
	prefix = bot.config["misc"]["command_prefix"][0]
	if len(args) == 0:
	    bot.reply("My commands are {0}help {0}claim {0}hoof {0}edit {0}findchar {0}delplayer {0}delchar {0}dbversion {0}techinfo {0}listchars {0}listallchars {0}randomhorse. Use {0}help <command> for more info on each one. Use {0}claim <name> to claim a character and then {0}edit <name> <attribute> <value> to edit them.".format(prefix))
	    return
	if args[0] == "claim":
	    bot.reply("{0}claim <charactername>: Claims a character as your own. No spaces allowed".format(prefix))
	elif args[0] == "hoof":
	    bot.reply("{0}hoof <charname> [attribute1] [attribute2] [...]: Look up a character or optionally specific attributes. See {0}help attributes".format(prefix))
	elif args[0] == "edit":
	    bot.reply("{0}edit <charname> <attribute> <value>: Set the attribute of a character you have claimed to <value>. Maximum length of 300 characters per <value>. See {0}help attributes. To unset an attribute, enter \".\" for the value.".format(prefix))
	elif args[0] == "delplayer":
	    bot.reply("{0}delplayer <playername>: Deletes all of <playername>'s characters from the database. Admin only.".format(prefix))
	elif args[0] == "delchar":
	    bot.reply("{0}delchar <charname>: Deletes <character> from the database. You must own the character or be a bot admin.".format(prefix))
	elif args[0] == "help":
	    bot.reply("{0}help [command]: Tells you how to use the bot.".format(prefix))
	elif args[0] == "attributes":
	    bot.reply("List of valid attributes: %s" % str.join(", ",self.attributes))
	elif args[0] == "listchars":
	    bot.reply("{0}listchars [playername]: Lists all of your characters or all of another player's characters.".format(prefix))
	elif args[0] == "listallchars":
	    bot.reply("{0}listallchars: Lists all characters and which accounts they are linked to in the database.".format(prefix))
	elif args[0] == "dbversion":
	    bot.reply("{0}dbversion: Returns the version of the db schema.".format(prefix))
	elif args[0] == "findchar":
	    bot.reply("{0}findchar [attribute] <search terms>: Searches the database for characters that match the search terms. Defaults to search by name if no attribute given.".format(prefix))
	elif args[0] == "techinfo":
	    bot.reply("{0}techinfo <charname>: Returns all the technical info about a character".format(prefix))
	elif args[0] == "randomhorse":
	    bot.reply("{0}randomhorse: Returns a random character(Filters coming later)".format(prefix))
	return

    def command_randomhorse(self, bot, event_args):
	accounts = self.get_accounts()
        if accounts == "":
            bot.reply("I have no characters stored.")
            return
        accounts = list(set(accounts))
	allchars = list()
        for account in accounts:
            allchars += self.get_chars(account)
	bot.reply(random.choice(allchars))

    def command_techinfo(self, bot, event_args):
	args = event_args["args"]
	if len(args) == 0:
	    bot.reply("You must specify a character")
	    return
	
	name = event_args["args"][0]

	if not self.check_char_exists(name):
            bot.reply("Character %s does not exist." % name)
            return

	c = self.dbconn.cursor()
	c.execute("SELECT nickserv_account,timestamp,creation_time FROM characters WHERE char_ircname = ? COLLATE NOCASE", (name,))
	data = c.fetchone()
	bot.reply("Nickserv account: %s Last editted: %s Created: %s" % (data[0],data[1],data[2]))

    def command_findchar(self, bot, event_args):
	args = event_args["args"]
	if len(args) == 0:
	    bot.reply("You must give a search term")
	    return

	if len(args) == 1:
	    for i in self.attributes:
		if args[0] == i:
		    bot.reply("You must enter something to search for.")
		    return
	    args.insert(0,"irc_name")

	#Generate the query string
	query = "SELECT char_ircname,nickserv_account FROM characters WHERE "
	for i in self.attributes:
	    if args[0] == i:
		query += self.attr_to_sql(i) + " LIKE ?"
		break
	c = self.dbconn.cursor()
        print query
	c.execute(query, ("%" + str.join("_",args[1:]) + "%",))
	rows = c.fetchall()

	if len(rows) == 0:
	    bot.reply("No matches found.")
	    return

	if len(rows) > 4:
	    bot.reply("Found %s matches, please narrow your search" % len(rows))
	    return

	replystring = "Found %s match(es):" % len(rows)
	for i in rows:
	    replystring += " Character: " + i[0] + " owned by: " + i[1] + ","
	bot.reply(replystring[:-1])

    def command_delplayer(self, bot, event_args):
	if not bot.check_permission("admin", ""):
	    bot.reply("Permission denied: You are not an admin.")
	    return
	args = event_args["args"]
	if len(args) == 0:
	    bot.reply("delplayer: Requires a username to delete.")
	    return
	account = args[0]
	if not self.check_account_exists(account):
	    bot.reply("Accounts %s doesn't exist." % account)
	    return
	characters = self.get_chars(account)
	self.del_account(account)
	bot.reply("Account " + account + " deleted. Characters deleted: {0}".format(str.join(", ", characters)))

    def command_listallchars(self, bot, event_args):
	#if not bot.check_permission("admin", ""):
	#    bot.reply("Permission denied: You are not an admin.")
	#    return
	#admin
	accounts = self.get_accounts()
	if accounts == "":
	    bot.reply("I have no characters stored.")
	    return
	accounts = list(set(accounts))
	bot.reply("All messages sent in query.")
	for account in accounts:
	    bot.privmsg(event_args["sender"], account + ": " + str.join(", ", self.get_chars(account)))

    def command_delchar(self, bot, event_args):
	name = event_args["args"][0]
	if not self.check_char_exists(name):
	    bot.reply("Character %s does not exist." % name)
	    return
	sender = event_args["sender"]
	if not bot.check_permission("admin", ""):
	    #not an admin, check if they own the character
	    queue_data = [event_args, 0]
            self.message_queue.append(queue_data)
	    bot.raw("WHOIS " + sender)
	    return
	#else admin, do it anyways
	self.do_delchar(bot, event_args, "", True)
	return

    def command_hoof(self, bot, event_args):
	#displays data about a character
	args = event_args["args"]
	if len(args) < 1:
	    bot.reply("Not enough parameters. .hoof <charname> [attribute1] [attribute2] [...]")
	    return
	#check for character existing
	name = str(args[0])
	if not self.check_char_exists(name):
	    bot.reply("Character %s does not exist." % name)
	    return
	if len(args) == 1 or len(args) > 3:
	    bot.reply("All data will be sent in query")	
	    if len(args) == 1:
		#all data
		attribute = self.attributes
	if len(args) > 1:
	    attribute = args[1:]
	    attribute = self.parse_attributes(list(set(attribute)))
	    attribute = list(set(attribute))
	    if len(attribute) == 0:
		bot.reply("No valid attributes given. Use \"{0}help attributes\" for a list of valid attributes, aborting".format(bot.config["misc"]["command_prefix"][0]))
		return

	#TODO: Clean up this junk
	sqlparams = self.parse_sqlattributes(attribute)
	sqlstring = ("SELECT %s FROM characters WHERE char_ircname = ? COLLATE NOCASE;" % self.sqllist_to_string(sqlparams))
	c = self.dbconn.cursor()
	c.execute(sqlstring, (name,))
	row = c.fetchone()
	sent = False
	if len(args) > 1 and len(args) < 4:
	#send data to source
	    i = 0
	    for message in row:
		if message and message != "":
		    bot.reply("%s: %s" % (self.sql_to_attr(sqlparams[i]),message))
		    sent = True
		i += 1
	    if not sent:
		bot.reply("%s: No data" % self.sql_to_attr(sqlparams[0]))
	    return
	#else data in query
	i = 0
	for message in row:
	    if message and message != "":
		bot.privmsg(event_args["sender"], "%s: %s" % (self.sql_to_attr(sqlparams[i]),message))
		sent = True
	    i += 1
	if not sent:
	    bot.reply("%s: No data" % self.sql_to_attr(sqlparams[0]))

    def command_claim(self, bot, event_args):
	if len(event_args["args"]) == 0:
	    bot.reply("You must enter a character name.")
	    return
	args = event_args["args"]
	if len(args[0]) > 32:
	    bot.reply("Character name is too long. Max length is 32 characters.")
	    return
	if self.check_char_exists(args[0]):
	    bot.reply("%s is already claimed." % args[0])
	    return
        if not self.valid_irc_name(args[0]):
            bot.reply("%s is not a valid irc nickname." % args[0])
            return
	queue_data = [event_args, 0]
	self.message_queue.append(queue_data)
	bot.raw("WHOIS " + event_args["sender"])

    def command_listchars(self, bot, event_args):
	args = event_args["args"]
	if len(args) > 0:
	    #specific user
	    self.do_listchars(bot, event_args, args[0])
	else:
	    #self
	    queue_data = [event_args, 0]
	    self.message_queue.append(queue_data)
	    bot.raw("WHOIS " + event_args["sender"])

    def command_edit(self, bot, event_args):
	#verify correct edit command before doing expensive whois
	args = event_args["args"]
	if len(args) < 3:
	    bot.reply("Not enough parameters. .edit <charname> <attribute> <value>")
	    return
	name = str(args[0])
	if not self.check_char_exists(name):
	    bot.reply("%s does not exist as a character." % name)
	    return
	if len(str.join(" ",args[2:])) > 300:
	    bot.reply("Maximum length for a value is 300 characters")
	    return

	attribute = str(args[1].lower())

	if attribute not in self.attributes:
	    bot.reply("%s is not a valid attribute. See \".help attributes\"" % attribute)
            return

	if attribute == "irc_name":
            if self.check_char_exists(args[2]):
                bot.reply("%s already exists as a character." % args[2])
	        return
            if not self.valid_irc_name(args[2]):
                bot.reply("%s is not a valid irc name." % args[2])
                return

	queue_data = [event_args, 0]
	self.message_queue.append(queue_data)
	bot.raw("WHOIS " + event_args["sender"])

    def handle_330(self, bot, event_args):
	#Do stuff on a whois return with a nickserv account
	accountname = event_args.params[2]
	nick = event_args.params[1]
	messagelist = list()
	for message in self.message_queue:
	    if message[0]["sender"] != nick:
                message[1] += 1
	        continue
	    else:
		command = message[0]["command"]
                try:
		    if(command == "claim"):
		        self.do_claim(bot, message[0], accountname)
		    elif(command == "edit"):
		        self.do_edit(bot, message[0], accountname)
		    elif(command == "delchar"):
		        self.do_delchar(bot, message[0], accountname)
		    elif(command == "listchars"):
		        self.do_listchars(bot, message[0], accountname)
                except Exception as e:
                    self.send_message(bot, message[0]["target"], message[0]["sender"], str(e))
		messagelist.append(message)
	for message in messagelist:
	    self.message_queue.remove(message)
	self.remove_stale()

    def remove_stale(self):
	#removes a single stale entry per run
	for message in self.message_queue:
	    if message[1] > 5:
		#Exceptions, but removes the one stale message
		#Something better?
	        self.message_queue.remove(message)

    def check_char_exists(self, name):
	#checks if the given character exists in the database
	c = self.dbconn.cursor()
	c.execute("SELECT * FROM characters WHERE char_ircname = ? COLLATE NOCASE;", (name,))
	if c.fetchone() == None:
	    return False
	return True

    def check_account_exists(self, accountname):
	#checks if the given account exists in the database
	c = self.dbconn.cursor()
	c.execute("SELECT * FROM characters WHERE nickserv_account = ? COLLATE NOCASE;", (accountname,))
	if c.fetchone() == None:
	    return False
	return True

    def check_ownership(self, name, accountname):
	#checks if accountname owns the character "name"
	c = self.dbconn.cursor()
	c.execute("SELECT nickserv_account FROM characters WHERE char_ircname = ? COLLATE NOCASE;", (name,))
	if c.fetchone()[0] == accountname:
	    return True
	return False

    def get_ownership(self, name):
	#gets account name of character's owner, returns "" on failure
	c = self.dbconn.cursor()
	c.execute("SELECT nickserv_account FROM characters WHERE char_ircname = ? COLLATE NOCASE;", (name,))
	return c.fetchone()

    def get_chars(self, accountname):
	#returns a list of all characters owned by a user
	c = self.dbconn.cursor()
	c.execute("SELECT char_ircname FROM characters WHERE nickserv_account = ? COLLATE NOCASE;", (accountname,))
	return [x[0] for x in c.fetchall()]

    def get_accounts(self):
	#returns a list of all accounts
	c = self.dbconn.cursor()
	c.execute("SELECT nickserv_account FROM characters;")
	return [x[0] for x in c.fetchall()]

    def do_delchar(self, bot, event_args, accountname, admin=False):
	#verify user if not an admin and delete character
	args = event_args["args"]
	name = args[0]
	
	if not admin:
	    #verify account
	    if not self.check_ownership(name, accountname):
		self.send_message(bot, event_args["target"], event_args["sender"], "You do not have permission to delete that character.")
		return
	#delete
	c = self.dbconn.cursor()
	c.execute("DELETE FROM characters WHERE char_ircname = ? COLLATE NOCASE;", (name,))
	self.dbconn.commit()
	self.send_message(bot, event_args["target"], event_args["sender"], "Successfully deleted character %s" % name)

    def del_account(self, accountname):
	c = self.dbconn.cursor()
	c.execute("DELETE FROM characters WHERE nickserv_account = ? COLLATE NOCASE;", (accountname,))
	self.dbconn.commit()

    def do_claim(self, bot, message, accountname):
	#claims a character and links it to their nickserv account
	name = str(message["args"][0])
	c = self.dbconn.cursor()
	c.execute("SELECT char_ircname,nickserv_account FROM characters WHERE char_ircname=? COLLATE NOCASE;", (name,))
	row = c.fetchone()
	if row is not None:
	    self.send_message(bot, message["target"], message["sender"], "%s has already been claimed by %s." % (row[0], row[1]))
	    return
	values = (str(name), str(accountname), datetime.datetime.now(), datetime.datetime.now())
	c.execute("INSERT INTO characters(char_ircname, nickserv_account, timestamp, creation_time) VALUES (?,?,?,?)", (values))
	self.dbconn.commit()
	self.send_message(bot, message["target"], message["sender"], "%s has claimed the character %s" % (message["sender"], message["args"][0]))
	return

    def do_edit(self, bot, event_args, accountname):
	#checks if a person has permission to edit a character then edits it
	args = event_args["args"]
	c = self.dbconn.cursor()
	name = str(args[0])
	if not self.check_ownership(name, accountname):
	    self.send_message(bot, event_args["target"], event_args["sender"],"You do not have permission to edit this character.")
	    return
	data = str.join(" ",args[2:])
	i = 0
	sqlstring = None
	if data == ".":
	    data = ""
	for attribute in self.attributes:
	    if attribute == str(args[1]).lower():
		sqlstring = ("UPDATE characters SET %s = ? WHERE char_ircname = ? COLLATE NOCASE;" % self.sqlattributes[i])
		break
	    i += 1

	c.execute(sqlstring, (data,name))
	c.execute("UPDATE characters SET timestamp = ? WHERE char_ircname = ? COLLATE NOCASE;", (datetime.datetime.now(),name))
	self.dbconn.commit()
	if data == "":
	    self.send_message(bot, event_args["target"], event_args["sender"], "Successfully removed %s." % str(args[1]))
	else:
	    self.send_message(bot, event_args["target"], event_args["sender"], "Successfully updated %s to %s" % (str(args[1]),data))
	return

    def do_listchars(self, bot, event_args, accountname):
	characters = self.get_chars(accountname)
	if characters:
	#they have at least one
	    self.send_message(bot, event_args["target"], event_args["sender"], "{0} has the following characters: {1}".format(str(accountname), str.join(", ", characters)))
	else:
	#no characters on that account name, check if character exists, then get owner to return
	    character = self.get_ownership(accountname)
	    if character == None:
		self.send_message(bot, event_args["target"], event_args["sender"], "%s has no characters." % accountname)
	    else:
		#that character is owned, return that data instead
		characters = self.get_chars(str(character[0]))
		self.send_message(bot, event_args["target"], event_args["sender"], "{0} is owned by {1}, who has the following characters: {2}".format(str(accountname), str(character[0]), str.join(", ", characters)))
	return
	

    def generate_sql_update(self, i):
	return ("UPDATE characters SET %s = ? WHERE char_ircname = ? COLLATE NOCASE;" % self.sqlattributes[i])

    def parse_attributes(self, message):
	#return a list of all the valid attributes
	attrs = []
	for attr in message:
	    if attr.lower() in self.attributes or attr.lower() == "long":
		attrs.append(attr.lower())
	return attrs
	
    def parse_sqlattributes(self, attributeslist):
	#return a list of all the valid sqlattribtes in attributes
	sqls = []
	for attr in attributeslist:
	    if self.attr_to_sql(attr) != "":
		sqls.append(self.attr_to_sql(attr))
	    if attr == "long":
		sqls.append("char_long1")
		sqls.append("char_long2")
		sqls.append("char_long3")
	return sqls

    def sqllist_to_string(self, sqllist):
	#return a string for use in a sql query for column names
	return str.join(",",sqllist)

    def attr_to_sql(self, attribute):
	i = 0
	for sql in self.attributes:
	    if sql == attribute:
		return self.sqlattributes[i]
	    i += 1
	return ""

    def sql_to_attr(self, sql):
        i = 0
        for attr in self.sqlattributes:
            if attr == sql:
                return self.attributes[i]
            i += 1
        return ""

    def send_message(self, bot, target, source, message):
	if target == bot.me["nicks"][0]:
	#query message
	    bot.privmsg(source,message)
	    return
	#channel message
	bot.privmsg(target,message)

    def valid_irc_name(self, nick):
        return re.match("^[A-Za-z_\-\[\]\\^{}|`][A-Za-z0-9_\-\[\]\\^{}|`]*$", nick)
