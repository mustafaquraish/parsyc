
def curried(orig, argc=None):
    if argc is None:
        if isinstance(orig, type):
            argc = orig.__init__.__code__.co_argcount - 1
        else:
            argc = orig.__code__.co_argcount
    def wrapped(*a):
        if len(a) == argc:
            return orig(*a)
        def q(*b):
            return orig(*(a + b))
        return curried(q, argc - len(a))
    return wrapped