import ssl
import select
import socket
import threading

from linebuffer import LineBuffer


class IRCConnection:
    def __init__(self, host, port, use_ssl=False):
        self.host = host
        self.port = port
        self.ssl = use_ssl
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer = LineBuffer()
        if self.ssl:
            self.socket = ssl.wrap_socket(self.socket)

        self.lock = threading.Lock()

    def connect(self):
        self.socket.connect((self.host, self.port))

    def disconnect(self):
        self.socket.close()

    def loop(self):
        readable, writable, errored = select.select([self.socket], [], [], 0.5)

        if readable:
            self.buffer.append(self.socket.recv(4096))

    def write_line(self, line):
        with self.lock:  # We use a lock here because some modules might call reply() from a new thread, which might end up breaking here.
            self.socket.send("%s\r\n" % line)
