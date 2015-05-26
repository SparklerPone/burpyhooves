from modules import Module
from collections import deque
import string
import sqlite3

class MuckModule(Module):
    name = "muck"
    description = "Character container"
    message_queue = deque()
    dbconn = 0
    attributes = [ "name", "sex", "species", "job", "age", "coat", "mane", "eyes", "cm", "orientation",
		   "height", "weight", "smell", "taste", "feel", "fetish", "short", "long1", "long2",
		   "long3"]
    sqlattributes = [ "char_name", "char_sex", "char_species", "char_job", "char_age", "char_coat",
		      "char_mane", "char_eyes", "char_cm", "char_orientation", "char_height",
		      "char_weight", "char_smell", "char_taste", "char_feel", "char_fetish",
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
	
	self.hook_command("claim", self.command_claim)
	self.hook_command("hoof", self.command_hoof)
	self.hook_command("help", self.command_help)
	self.hook_command("edit", self.command_edit)
	self.hook_command("delplayer", self.command_delplayer)
	self.hook_command("delchar", self.command_delchar)
	self.hook_numeric("330", self.handle_330)

    def command_help(self, bot, event_args):
	if len(event_args["args"]) == 0:
	    bot.reply("My commands are .help .claim .hoof .edit .delplayer .delchar. Use .help <command> for more info on each one.")
	    return
	if event_args["args"][0] == "claim":
	    bot.reply(".claim <charactername>: Claims a character as your own. No spaces allowed")
	elif event_args["args"][0] == "hoof":
	    bot.reply(".hoof <charname> [attribute1] [attribute2] [...]: Look up a character or optionally specific attributes. See .help attributes")
	elif event_args["args"][0] == "edit":
	    bot.reply(".edit <charname> <attribute> <value>: Set the attribute of a character you have claimed to <value>. Maximum length of 200 characters per <value>. See .help attributes")
	elif event_args["args"][0] == "delplayer":
	    bot.reply(".delplayer <playername>: Deletes all of <playername>'s characters from the database. Admin only.")
	elif event_args["args"][0] == "delchar":
	    bot.reply(".delchar <charname>: Deletes <character> from the database. Admin only.")
	elif event_args["args"][0] == "help":
	    bot.reply(".help [command]: Tells you how to use the bot.")
	elif event_args["args"][0] == "attributes":
	    bot.reply("List of valid attributes: %s" % str.join(", ",self.attributes))
	return

    def command_delplayer(self, bot, event_args):
	bot.reply("Admin command to delete a player from the db, NYI")
	return

    def command_delchar(self, bot, event_args):
        bot.reply("Admin command to delete a character from the db, NYI")
	
        return

    def command_hoof(self, bot, event_args):
	#displays data about a character
	if len(event_args["args"]) < 1:
	    bot.reply("Not enough parameters. .hoof <charname> [attribute1] [attribute2] [...]")
	    return
	#check for character existing
	name = str(event_args["args"][0])
	c = self.dbconn.cursor()
	c.execute("SELECT char_name FROM characters WHERE char_name=? COLLATE NOCASE;", (name,))
	row = c.fetchone()

	if row is None:
	    bot.reply("Character %s does not exist." % name)
	    return
	if len(event_args["args"]) == 1 or len(event_args["args"]) > 3:
	    bot.reply("All data will be sent in query")	
	    if len(event_args["args"]) == 1:
		#all data
		attribute = self.attributes
	if len(event_args["args"]) > 1:
	    attribute = event_args["args"][1:]
	    attribute = self.parse_attributes(list(set(attribute)))
	    if len(attribute) == 0:
		bot.reply("No valid attributes given, aborting")
		return

	sqlparams = self.parse_sqlattributes(attribute)
	sqlstring = ("SELECT %s FROM characters WHERE char_name = ? COLLATE NOCASE;" % self.sqllist_to_string(sqlparams))
	c.execute(sqlstring, (name,))
	row = c.fetchone()
	if len(event_args["args"]) > 1 and len(event_args["args"]) < 4:
	#send data to source
	    i = 0
	    for message in row:
		if message != "":
		    bot.reply("%s: %s" % (self.sql_to_attr(sqlparams[i]),message))
		i += 1
	    return
	#else data in query
	i = 0
	for message in row:
	    if message != "":
		bot.privmsg(event_args["sender"], "%s: %s" % (self.sql_to_attr(sqlparams[i]),message))
	    i += 1


    def command_claim(self, bot, event_args):
	queue_data = [event_args, 0]
	self.message_queue.append(queue_data)
	bot.raw("WHOIS " + event_args["sender"])

    def command_edit(self, bot, event_args):
	#verify correct edit command before doing expensive whois
	if len(event_args["args"]) < 3:
	    bot.reply("Not enough parameters. .edit <charname> <attribute> <value>")
	    return
	name = str(event_args["args"][0]).lower()
	c = self.dbconn.cursor()
	c.execute("SELECT char_name FROM characters WHERE char_name=? COLLATE NOCASE;", (name,))
	row = c.fetchone()
	if row is None:
	    bot.reply("%s does not exist as a character." % name)
	    return
	if len(str.join("",event_args["args"][2:])) > 200:
	    bot.reply("Maximum length for a value is 200 characters")
	    return

	attribute = str(event_args["args"][1].lower())

	if attribute not in self.attributes:
	    bot.reply("%s is not a valid attribute." % attribute)
            return

	if attribute == "name":
	    bot.reply("You may not change your name.")
	    return

	queue_data = [event_args, 0]
	self.message_queue.append(queue_data)
	bot.raw("WHOIS " + event_args["sender"])

    def handle_330(self, bot, event_args):
	accountname = event_args.params[2]
	nick = event_args.params[1]
	for message in self.message_queue:
	    if message[0]["sender"] != nick:
                message[1] += 1
	        continue
	    else:
		if(message[0]["command"] == "claim"):
		    self.do_claim(bot, message, accountname)
		elif(message[0]["command"] == "edit"):
		    self.do_edit(bot, message, accountname)
		break
	self.message_queue.remove(message)
	self.remove_stale()

    def remove_stale(self):
	#removes a single stale entry per run
	for message in self.message_queue:
	    if message[1] > 5:
	        self.message_queue.remove(message)

    def do_claim(self, bot, message, accountname):
	#claims a character and links it to their nickserv account
	name = str(message[0]["args"][0])
	c = self.dbconn.cursor()
	c.execute("SELECT char_name,nickserv_account FROM characters WHERE char_name=? COLLATE NOCASE;", (name,))
	row = c.fetchone()
	if row is not None:
	    self.send_message(bot, message[0]["target"], message[0]["sender"], "%s has already been claimed by %s." % (row[0], row[1]))
	    return
	values = (str(name), "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", str(accountname))
	c.execute("INSERT INTO characters VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (values))
	self.dbconn.commit()
	print(message[0]["sender"] + message[0]["args"][0] + message[0]["target"])
	self.send_message(bot, message[0]["target"], message[0]["sender"], "%s has claimed the character %s" % (message[0]["sender"], message[0]["args"][0]))
	return

    def do_edit(self, bot, message, accountname):
	#checks if a person has permission to edit a character then edits it
	c = self.dbconn.cursor()
	name = str(message[0]["args"][0]).lower()
	c.execute("SELECT char_name,nickserv_account FROM characters WHERE char_name=? COLLATE NOCASE;", (name,))
	row = c.fetchone()
	if accountname != row[1]:
	    self.send_message(bot, message[0]["target"], message[0]["sender"],"You do not have permission to edit this character. It is owned by %s" % row[1])
	    return
	data = str.join(" ",message[0]["args"][2:])
	i = 0
	sqlstring = None
	for attribute in self.attributes:
	    if attribute == str(message[0]["args"][1]):
		sqlstring = self.generate_sql_update(i)
		break
	    i += 1
	c.execute(sqlstring, (data,name))
	self.dbconn.commit()
	self.send_message(bot, message[0]["target"], message[0]["sender"], "Successfully updated %s to %s" % (str(message[0]["args"][1]),data))
	return

    def generate_sql_update(self, i):
	return ("UPDATE characters SET %s = ? WHERE char_name = ? COLLATE NOCASE;" % self.sqlattributes[i])

    def parse_attributes(self, message):
	#return a list of all the valid attributes
	attrs = []
	for attr in message:
	    if attr in self.attributes:
		attrs.append(attr)
	return attrs
	
    def parse_sqlattributes(self, attributeslist):
	#return a list of all the valid sqlattribtes in attributes
	sqls = []
	for attr in attributeslist:
	    if self.attr_to_sql(attr) != "":
		sqls.append(self.attr_to_sql(attr))
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
