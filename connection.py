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
import ssl
import time
import socks
import select
import socket
import logging
import threading

from urlparse import urlparse
from linebuffer import LineBuffer


class IRCConnection:
    def __init__(self, host, port, use_ssl=False, proxy=None, sendq_delay=0):
        self.host = host
        self.port = port
        self.ssl = use_ssl
        self.socket = None
        self._setup_sockets(use_ssl, proxy)
        self.buffer = LineBuffer()
        self.lock = threading.Lock()
        self.sendq = []
        self.sendq_delay = sendq_delay
        self.last_send = 0.0

    def connect(self):
        self.socket.connect((self.host, self.port))
        if isinstance(self.socket, ssl.SSLSocket):
            self.socket.do_handshake(True)

    def disconnect(self):
        self.socket.close()

    def loop(self):
        self.handle_queue()
        readable, writable, errored = select.select([self.socket], [], [], 0.1)

        if readable:
            data = self.socket.recv(4096)
            if data == "":
                logging.error("Server closed our connection unexpectedly!")
                return False
            self.buffer.append(data)

        return True

    def write_line(self, line, force=False):
        with self.lock:  # We use a lock here because some modules might call reply() from a new thread, which might end up breaking here.
            if force:
                self.socket.send("%s\r\n" % line)
            else:
                self.sendq.append(line)

    def handle_queue(self):
        with self.lock:
            if self.sendq:
                now = time.time()
                if (now - self.last_send) >= self.sendq_delay:
                    self.socket.send("%s\r\n" % self.sendq.pop(0).decode('utf-8'))
                    self.last_send = now

    def _setup_sockets(self, use_ssl, proxy):
        sock = None
        _sock = None
        if proxy:
            u = urlparse(proxy)
            proxy_type = getattr(socks, "PROXY_TYPE_%s" % u.scheme.upper())
            split_netloc = u.netloc.split(":")
            proxy_host = split_netloc[0]
            proxy_port = int(split_netloc[1])
            sock = socks.socksocket()
            sock.setproxy(proxy_type, proxy_host, proxy_port, rdns=True)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _sock = sock

        if use_ssl:
            sock = ssl.SSLSocket(sock, do_handshake_on_connect=False)
            # Trust me, I'm a doctor.
            sock.connect = _sock.connect
            sock._sslobj = sock._context._wrap_socket(sock._sock, sock.server_side, sock.server_hostname, ssl_sock=sock)

        self.socket = sock
