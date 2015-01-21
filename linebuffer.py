class LineBuffer:
    def __init__(self, data=""):
        self.data = data

    def append(self, data):
        self.data += data

    def has_line(self):
        return "\n" in self.data

    def pop_line(self):
        if not self.has_line():
            return None

        lines = self.data.split("\n")
        line = lines.pop(0)
        self.data = "\n".join(lines)
        return line.strip()

    def flush(self):
        temp = self.data
        self.data = ""
        return temp

    def __iter__(self):
        return self

    def next(self):
        if self.has_line():
            return self.pop_line()

        raise StopIteration