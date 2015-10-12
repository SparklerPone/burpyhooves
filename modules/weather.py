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
import urllib
import threading
import socks
import socket
import json

from bs4 import BeautifulSoup
from modules import Module


class WeatherModule(Module):
    name = "Weather"
    description = "Gets the weather from yahoo API."

    def module_init(self, bot):
        self.hook_command("w", self.handle_w)

    def handle_w(self, bot, event_args):
        reply_to = event_args["target"]
        if event_args["target"] == bot.me["nicks"][0]:
            reply_to = event_args["sender"]
        
        url = "https://query.yahooapis.com/v1/public/yql?q="
        query = "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text=\"%s\")" % " ".join(event_args["args"])
        url = url + urllib.quote("%s" % query, "*()&=") + "&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys"
        t = TitleFetchThread(url, lambda resp: bot.privmsg(reply_to, resp), self, " ".join(event_args["args"]))
        t.start()



class TitleFetchThread(threading.Thread):
    def __init__(self, url, reply_func, module, place):
        super(TitleFetchThread, self).__init__()
        self.url = url
        self.reply_func = reply_func
        self.module = module
        self.place = place

    def run(self):
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
        socket.socket = socks.socksocket

        try:
            data = self.get_data()
        except RuntimeError as e:
            #No data
            print str(e)
            return
        yahooweather = json.load(data)
        try:
            weather = yahooweather["query"]["results"]["channel"]
        except Exception as e:
            self.reply_func("Could not get weather for " + self.place)
            return
        location = yahooweather["query"]["results"]["channel"]["location"]
        temperature = weather["item"]["condition"]["temp"]
        ctemperature = int((int(temperature) - 32)*.55)
        wind = int(weather["wind"]["speed"])
	kwind = int(wind*1.609344)
        self.reply_func("Weather for " + location["city"] + " " + location["region"] + ", " + location["country"] + ": [Temperature: " + temperature + weather["units"]["temperature"] + "(" + str(ctemperature) + "C)] [Condition: " + weather["item"]["condition"]["text"] + "] [Wind Speed: " + str(wind) + weather["units"]["speed"] + "(" + str(kwind) + "km/h)]")
#        if hasattr(soup, "title") and soup.title is not None:
#            self.reply_func("[ %s ]" % (soup.title.text.strip().replace("\r", "").replace("\n", "")[:128]))

    def get_data(self):
        try:
            request = urllib2.Request(self.url)
            data = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            print e
            return e.fp.read()
        except Exception as e:
            logging.error("urltitle: Error fetching title for URL '%s': %s" % (self.url, str(e)))
            raise RunTimeError("urltitle: Error fetching title for URL '" + self.url +"': " + str(e))
        return data

    def send_message(self, bot, target, source, message):
        if target == bot.me["nicks"][0]:
        #query message
            bot.privmsg(source,message)
            return
        #channel message
        bot.privmsg(target,message)
