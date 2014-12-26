class AttrDict(dict):
    """
    A simple ict subclass allowing attribute access.
    """
    def __init__(self, orig):
        dict.__init__(orig)

    def __getattr__(self, item):
        retval = self.__getitem__(item)
        if isinstance(retval, dict) and not isinstance(retval, AttrDict):
            return AttrDict(retval)
        return retval

    def __setattr__(self, key, value):
        return self.__setitem__(key, value)
