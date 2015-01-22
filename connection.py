import ssl
import socks
import select
import socket
import logging
import threading

from urlparse import urlparse
from linebuffer import LineBuffer


class IRCConnection:
    def __init__(self, host, port, use_ssl=False, proxy=None):
        self.host = host
        self.port = port
        self.ssl = use_ssl
        self.socket = None
        self._setup_sockets(use_ssl, proxy)
        self.buffer = LineBuffer()
        self.lock = threading.Lock()

    def connect(self):
        self.socket.connect((self.host, self.port))
        if isinstance(self.socket, ssl.SSLSocket):
            self.socket.do_handshake(True)

    def disconnect(self):
        self.socket.close()

    def loop(self):
        readable, writable, errored = select.select([self.socket], [], [], 0.5)

        if readable:
            data = self.socket.recv(4096)
            if data == "":
                logging.error("Server closed our connection unexpectedly!")
                return False
            self.buffer.append(data)

        return True

    def write_line(self, line):
        with self.lock:  # We use a lock here because some modules might call reply() from a new thread, which might end up breaking here.
            self.socket.send("%s\r\n" % line)

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
