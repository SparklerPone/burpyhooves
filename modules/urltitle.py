#!/usr/bin/python2
# -*- coding: utf-8 -*-
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
import json

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
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
        socket.socket = socks.socksocket

        if re.match("^https?://(www\.)?(derpiboo(ru\.org|\.ru)|ronxgr5zb4dkwdpt\.onion|derpicdn.net)/.+", self.url):
            self.handle_derpibooru()
            return

        try:
            data = self.get_data()
        except RuntimeError as e:
            #No data
            print str(e)
            return
        soup = BeautifulSoup(data)
        if hasattr(soup, "title") and soup.title is not None:
            self.reply_func("[ %s ]" % (soup.title.text.strip().replace("\r", "").replace("\n", "")[:128]))

    def get_data(self):
        try:
            request = urllib2.Request(self.url)
            data = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            return e.fp.read()
        except Exception as e:
            logging.error("urltitle: Error fetching title for URL '%s': %s" % (self.url, str(e)))
            raise RunTimeError("urltitle: Error fetching title for URL '" + self.url +"': " + str(e))
        return data

    def handle_derpibooru(self):
        onion = False
        if "ronxgr5zb4dkwdpt.onion" in self.url:
            self.url = self.url.replace("ronxgr5zb4dkwdpt.onion", "derpiboo.ru")
            onion = True
        elif "derpicdn.net" in self.url:
            match = re.match("https?://derpicdn.net/img/view/\d+/\d+/\d+/(\d+).*", self.url)
            self.url = "https://derpiboo.ru/" + match.group(1)
        match = re.match("^([^?]+)", self.url)
        self.url = match.group(1) + ".json"
        try:
            data = self.get_data()
        except RunTimeError as e:
            self.reply_func("urltitle: Error fetching data for URL '%s': %s" % (self.url, str(e)))
            logging.error("urltitle: Error fetching data for URL '%s': %s" % (self.url, str(e)))
            return
        except Exception as e:
            logging.error("urltitle: Error fetching title for URL '%s': %s" % (self.url, str(e)))
            return

        derpiresponse = json.load(data)
        artist = ""
        taglist = derpiresponse["tags"].split(", ")
        for tag in taglist:
            if tag == "explicit" or tag == "safe" or tag == "questionable" or tag == "suggestive" or tag == "grimdark" or tag == "semi-grimdark":                                                                                                          rating = tag
            if tag.startswith(u"artist:"):
                 artist = artist + " " + tag[7:]
        if not artist:
            artist = "Unknown"
        deltaglist = list()
        for tag in taglist:
            if tag.startswith("artist:"):
                deltaglist.append(tag)
            elif tag == "explicit" or tag == "safe" or tag == "questionable" or tag == "suggestive" or tag == "grimdark" or tag == "semi-grimdark":
                deltaglist.append(tag)
        for tag in deltaglist:
            taglist.remove(tag)
        tagcount = len(taglist)
        more = ""
        if tagcount > 7:
            more = " + %s more" % str(tagcount - 7)
        tags = taglist[:7]
        tagsfinal = ", ".join(tags)
        response = "Derpibooru image #" + str(derpiresponse["id_number"]) + ":"
        if onion:
            response = response + " [URL: " + self.url[:-5] + "] "
        if int(derpiresponse["upvotes"] + derpiresponse["downvotes"]) != 0:
            percent = int(float(derpiresponse["upvotes"]) / float(derpiresponse["upvotes"] + derpiresponse["downvotes"] ) * 100)
        else:
            percent = "NaN"
        response = response + " [Rating: " + rating + "] [Artist:" + artist + "] [Score: ▲".decode('utf-8') + str(derpiresponse["upvotes"]) + "/▼".decode('utf-8') + str(derpiresponse["downvotes"]) + "=" + str(derpiresponse["score"]) + "(" + str(percent) + "%)] [Tags: " + tagsfinal + more + "]"
        self.reply_func(response)
