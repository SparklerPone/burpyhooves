import re
import logging
import urllib2
import threading

from bs4 import BeautifulSoup
from modules import Module


class TitleModule(Module):
    name = "URLTitle"
    description = "Automatically gets titles of URLs posted in channels."

    def module_init(self, bot):
        self.hook_numeric("PRIVMSG", self.on_privmsg)

    def on_privmsg(self, bot, ln):
        sender = ln.hostmask.nick
        message = ln.params[-1]
        reply_to = sender
        if ln.params[0][0] == "#":
            reply_to = ln.params[0]
        match = re.match(".*(http(s)?://[^ ]+).*", message)
        if match:
            url = match.group(1)
            t = TitleFetchThread(url, lambda resp: bot.privmsg(reply_to, resp), self)
            t.start()


class TitleFetchThread(threading.Thread):
    def __init__(self, url, reply_func, module):
        super(TitleFetchThread, self).__init__()
        self.url = url
        self.reply_func = reply_func
        self.module = module

    def run(self):
        try:
            res = self.module.bot.http_get(self.url, stream=True, timeout=5.0)
            data = next(res.iter_content(4096))
        except Exception as e:
            logging.error("urltitle: Error fetching title for URL '%s': %s" % (self.url, str(e)))
            return

        soup = BeautifulSoup(data)
        if hasattr(soup, "title") and soup.title is not None:
            safe_title = soup.title.text.strip().replace("\r", "").replace("\n", "")[:128]
            self.reply_func("[ %s ] - %s" % (safe_title, self.url))