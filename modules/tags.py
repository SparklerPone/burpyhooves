from modules import Module

class TagsModule(Module):
    name = "Tags"
    description = "Provides support for adding 'tags' to users. (RP preferences and such.)"

    def module_init(self, bot):
        self.hook_command("tagadd", self.on_command_tagadd)
        self.hook_command("tagremove", self.on_command_tagremove)
        self.hook_command("tagclear", self.on_command_tagclear)

        self.hook_event("PRIVMSG", self.on_privmsg)

        bot.db.execute("CREATE TABLE IF NOT EXISTS tags (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, tag TEXT)")
        bot.db.execute("CREATE INDEX IF NOT EXISTS tags_user_index ON tags (user)")

    def _parse_tags(self, ln, args):
        tags = []
        user = ""
        if len(args) == 1:
            user = ln.hostmask.nick
            tags = [tag.strip() for tag in args[0].split("|")]
        else:
            user = args[0]
            tags = [tag.strip() for tag in " ".join(args[1:]).split("|")]

        return user, tags

    def on_command_tagadd(self, bot, ln, args):
        if not bot.check_condition(len(args) > 0, "Please specify a tag to add or a user to add a tag to and a tag to add!"):
            return

        user, tags = self._parse_tags(ln, args)

        for tag in tags:
            res = bot.db.execute_returnable("SELECT COUNT(*) FROM tags WHERE LOWER(user)=? AND LOWER(tag)=?", (user.lower(), tag.lower()))
            count = int(res.fetchone()["COUNT(*)"])
            if count == 0:
                bot.db.execute("INSERT INTO tags (user, tag) VALUES (?, ?)", (user, tag))

        tags_str = "that tag" if len(tags) == 1 else "those tags"
        bot.reply("I have added %s for you." % tags_str)

    def on_command_tagremove(self, bot, ln, args):
        if not bot.check_condition(len(args) > 0, "Please specify a tag to remove or a user to remove a tag from and a tag to add!"):
            return

        user, tags = self._parse_tags(ln, args)

        for tag in tags:
            bot.db.execute("DELETE FROM tags WHERE LOWER(user)=? AND LOWER(tag)=?", (user.lower(), tag.lower()))

        tags_str = "that tag" if len(tags) == 1 else "those tags"
        bot.reply("I have removed %s for you." % tags_str)

    def on_command_tagclear(self, bot, ln, args):
        user = ln.hostmask.nick
        if len(args) > 0:
            user = args[0]

        bot.db.execute("DELETE FROM tags WHERE LOWER(user)=?", (user.lower(),))

        bot.reply("I have cleared %s's tags for you." % user)

    def on_privmsg(self, bot, ln):
        message = ln.params[-1].strip()
        if len(message) >= 2 and message[0] == "?":
            user = message[1:]
            res = bot.db.execute_returnable("SELECT * FROM tags WHERE LOWER(user)=?", (user.lower(),))
            rows = res.fetchall()
            if len(rows) > 0:
                bot.reply("\x02%s\x02 has the following tags: %s" % (rows[0]["user"], " | ".join([row["tag"] for row in rows])))