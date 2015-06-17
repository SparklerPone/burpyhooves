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

class TagsModule(Module):
    name = "Tags"
    description = "Provides support for adding 'tags' to users. (RP preferences and such.)"

    def module_init(self, bot):
        self.hook_command("tagadd", self.on_command_tagadd)
        self.hook_command("tagremove", self.on_command_tagremove)
        self.hook_command("tagclear", self.on_command_tagclear)

        self.hook_numeric("PRIVMSG", self.on_privmsg)

        bot.db.execute("CREATE TABLE IF NOT EXISTS tags (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, tag TEXT)")
        bot.db.execute("CREATE INDEX IF NOT EXISTS tags_user_index ON tags (user)")

    def _parse_tags(self, ln, args):
        tags = []
        user = ""
        if len(args) == 1:
            user = ln.hostmask.nick
            tags = [tag.strip() for tag in " ".join(args).split("|")]
        else:
            user = args[0]
            tags = [tag.strip() for tag in " ".join(args[1:]).split("|")]

        return user, tags

    def on_command_tagadd(self, bot, event_args):
        args = event_args["args"]
        ln = event_args["ln"]
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

    def on_command_tagremove(self, bot, event_args):
        args = event_args["args"]
        ln = event_args["ln"]
        if not bot.check_condition(len(args) > 0, "Please specify a tag to remove or a user to remove a tag from and a tag to remove!"):
            return

        user, tags = self._parse_tags(ln, args)

        for tag in tags:
            bot.db.execute("DELETE FROM tags WHERE LOWER(user)=? AND LOWER(tag)=?", (user.lower(), tag.lower()))

        tags_str = "that tag" if len(tags) == 1 else "those tags"
        bot.reply("I have removed %s for you." % tags_str)

    def on_command_tagclear(self, bot, event_args):
        args = event_args["args"]
        ln = event_args["ln"]
        user = ln.hostmask.nick
        if len(args) > 0:
            user = args[0]

        if user.lower() != ln.hostmask.nick.lower() and (not bot.check_permission("admin", "You must be an admin to clear tags that are not attached to your nick!")):
            return

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
