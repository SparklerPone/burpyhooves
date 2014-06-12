#!/usr/bin/env python3
# Copyright (c) 2013 Andrew Wilcox.  All rights reserved.
# This file is part of glorircd.  See the LICENSE.md file for copyright info.

from itertools import takewhile
from functools import reduce
import operator


class Tags:
    __slots__ = ('tags', 'tagstr')

    """ Stores tags """

    def __init__(self, **kwargs):
        self.tags = kwargs.get('tags', None)
        self.tagstr = kwargs.get('tagstr', None)

        if not self.tags:
            self = self.parse(self.tagstr)

    """ Parse a raw tag string into a nice object. """
    @classmethod
    def parse(cls, raw):
        tags = dict()

        for tag in raw.split(';'):
            key, s, value = tag.partition('=')
            if value == '':
                value = None
            tags[key] = value

        return cls(tags=tags, tagstr=raw)


class Hostmask:
    __slots__ = ('nick', 'user', 'host', 'maskstr')

    """ Stores a user hostmask

    >>> repr(Hostmask.parse(mask='dongs!cocks@lol.org'))
    'Hostmask(dongs!cocks@lol.org)'
    >>> repr(Hostmask.parse(mask='dongs@lol.org'))
    'Hostmask(dongs@lol.org)'
    >>> repr(Hostmask.parse(mask='lol.org'))
    'Hostmask(lol.org)'
    """
    def __init__(self, **kwargs):
        self.nick = kwargs.get('nick', None)
        self.user = kwargs.get('user', None)
        self.host = kwargs.get('host', None)
        self.maskstr = kwargs.get('mask', None)

        if not any((self.nick, self.user, self.host)) and self.maskstr:
            self = self.parse(self.maskstr)

    """ Parse a raw hostmask into a nice object. """
    @classmethod
    def parse(cls, raw):
        if len(raw) == 0:
            return None

        host_sep = raw.find('@')
        has_other = (host_sep != -1)

        if not has_other:
            return cls(host=raw, mask=raw)

        nick_sep = raw.find('!')
        has_user = (nick_sep != -1)
        if not has_user:
            return cls(nick=raw[:host_sep], host=raw[host_sep + 1:],
                       mask=raw)
        else:
            return cls(nick=raw[:nick_sep],
                       user=raw[nick_sep + 1:host_sep],
                       host=raw[host_sep + 1:], mask=raw)

    def __str__(self):
        if not self.maskstr:
            if not any((self.nick, self.user, self.host)):
                self.maskstr = ''

            if self.nick and not self.host:
                # Nick only
                self.maskstr = self.nick

            elif not self.nick and self.host:
                # Host only
                self.maskstr = self.host
            else:
                # Both
                if self.user:
                    self.maskstr = self.nick + '!' + self.user + '@' + self.host
                else:
                    self.maskstr = self.nick + '@' + self.host

        return self.maskstr

    def __bytes__(self):
        return str(self).encode('utf-8', 'replace')

    def __repr__(self):
        return 'Hostmask({})'.format(str(self))


class Line:
    __slots__ = ('tags', 'hostmask', 'command', 'params', 'linestr',
                 'cancelled')

    """ Stores an IRC line.

    >>> repr(Line.parse(':lol.org PRIVMSG'))
    'Line(:lol.org PRIVMSG)'
    >>> repr(Line.parse('PING'))
    'Line(PING)'
    >>> repr(Line.parse('PING Elizacat'))
    'Line(PING Elizacat)'
    >>> repr(Line.parse('PING Elizacat :dongs'))
    'Line(PING Elizacat :dongs)'
    >>> repr(Line.parse('PING :dongs'))
    'Line(PING :dongs)'
    >>> repr(Line.parse(':dongs!dongs@lol.org PRIVMSG loldongs meow :dongs'))
    'Line(:dongs!dongs@lol.org PRIVMSG loldongs meow :dongs)'
    """
    def __init__(self, **kwargs):
        self.tags = kwargs.get('tags', None)
        self.hostmask = kwargs.get('host', None)
        self.command = kwargs.get('command', None)
        self.params = kwargs.get('params', list())
        self.linestr = kwargs.get('line', None)

        if not any((self.tags, self.hostmask, self.command, self.params)) and self.linestr:
            self = self.parse(self.linestr)
        else:
            if isinstance(self.tags, str):
                self.tags = Tags.parse(self.tags)

            if isinstance(self.hostmask, str):
                self.hostmask = Hostmask.parse(self.hostmask)

        self.cancelled = False

    """ Parse an IRC line.

    100% regex free, thanks to a certain fox.

    Also should raise on any invalid line.  It will be quite liberal with
    hostmasks (accepting such joys as '' and 'user1@user2@user3'), but trying
    to enforce strict validity in hostmasks will be slow. """
    @classmethod
    def parse(cls, line):
        raw_line = line
        tags = None
        hostmask = None
        params = list()

        # Do we have tags?
        if line[0] == '@':
            space = line.index(' ')  # Grab the separator
            tags = Tags.parse(line[1:space])
            line = line[space:].lstrip()

        # Do we have a hostmask?
        if line[0] == ':':
            space = line.index(' ')  # Grab the separator
            hostmask = Hostmask.parse(line[1:space])
            line = line[space:].lstrip()

        # Grab command
        command = reduce(operator.concat,
                         takewhile(lambda char: char not in (' ', ':'), line))
        assert len(command) > 0

        line = line[len(command):].lstrip().rstrip('\r\n')

        # Retrieve parameters
        while len(line) > 0:
            next_param = ''
            line = line.lstrip()

            if line[0] == ':':
                next_param = line[1:]
                line = ''
            else:
                next_param = reduce(operator.concat,
                                    takewhile(lambda char: char != ' ', line))
                line = line[len(next_param):]

            params.append(next_param)

        return cls(tags=tags, host=hostmask, command=command, params=params,
                   line=raw_line)

    def __str__(self):
        if not self.linestr:
            line = []
            if self.hostmask:
                line.append(':' + str(self.hostmask))

            if isinstance(self.command, str):
                line.append(self.command)
            else:
                line.append(self.command.value)

            if self.params:
                if any(x in (' ', ':') for x in self.params[-1]) and self.command != '004':
                    line.extend(self.params[:-1])
                    line.append(':' + self.params[-1])
                else:
                    line.extend(self.params)

            self.linestr = ' '.join(line) + '\r\n'

        return self.linestr

    def __bytes__(self):
        return str(self).encode('utf-8', 'replace')

    def __repr__(self):
        return 'Line({})'.format(str(self).rstrip('\r\n'))

    def __hash__(self):
        return hash(str(self))

import doctest
doctest.testmod()
if __name__ == '__main__':
    import doctest
    doctest.testmod()

