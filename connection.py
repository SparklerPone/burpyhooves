import ssl
import select
import socket

from line import Line

class IRCConnection:
	def __init__(self, host, port, use_ssl=False):
		self.host = host
		self.port = port
		self.ssl = use_ssl
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if self.ssl:
			self.socket = ssl.wrap_socket(self.socket)

		self.readbuffer = ""
		self.buffer = []
		self.last_line = None

	def connect(self):
		self.socket.connect((self.host, self.port))

	def disconnect(self):
		self.socket.close()

	def _read_line(self, the_socket):
		line = ""
		while 1:
			c = the_socket.recv(1)
			if c == "\n":
				return line.strip()
			if c is None:
				return None
			line += c

	def loop(self):
		self.last_line = None
		readable, writable, errored = select.select([self.socket], [], [], 0.5)
		if readable:
			sock = readable[0]
			raw_line = self._read_line(sock)
			line = Line.parse(raw_line)
			self.last_line = line

	def has_line(self):
		return self.last_line is not None

	def write_line(self, line):
		self.socket.send("%s\r\n" % line)
