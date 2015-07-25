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
import re
import logging
import urllib2
import threading
import socks
import socket

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

#    def run(self):
#        try:
#            res = self.module.bot.http_get(self.url, timeout=5.0)
#            data = next(res.iter_content(4096))
#        except Exception as e:
#            logging.error("urltitle: Error fetching title for URL '%s': %s" % (self.url, str(e)))
#            return
#
#        soup = BeautifulSoup(data)
#        if hasattr(soup, "title") and soup.title is not None:
#            safe_title = soup.title.text.strip().replace("\r", "").replace("\n", "")[:128]
#            self.reply_func("[ %s ] - %s" % (safe_title, self.url))

    def run(self):
#	s = socks.socksocket()
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
        socket.socket = socks.socksocket
#	s.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
	

        try:
                request = urllib2.Request(self.url)
#               request.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36')
                data = urllib2.urlopen(request)

        except urllib2.HTTPError as e:
            soup = BeautifulSoup(e.fp.read())
            if hasattr(soup, "title") and soup.title is not None:
                self.reply_func("[ %s ]" % (soup.title.text.strip().replace("\r", "").replace("\n", "")[:128]))
                return
            else:
                logging.error("urltitle: Error fetching title for URL '%s': %s" % (self.url, str(e)))
                self.reply_func("urltitle: Error fetching title for URL '%s': %s" % (self.url, str(e)))
                return

        except Exception as e:
            logging.error("urltitle: Error fetching title for URL '%s': %s" % (self.url, str(e)))
#           self.reply_func("urltitle: Error fetching title for URL '%s': %s" % (self.url, str(e)))
            return

        soup = BeautifulSoup(data)
        if hasattr(soup, "title") and soup.title is not None:
            self.reply_func("[ %s ]" % (soup.title.text.strip().replace("\r", "").replace("\n", "")[:128]))
