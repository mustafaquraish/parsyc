
def curried(orig, argc=None):
    if argc is None:
        if isinstance(orig, type):
            argc = orig.__init__.__code__.co_argcount - 1
        else:
            argc = orig.__code__.co_argcount
    def wrapper(*a):
        if len(a) == argc:
            return orig(*a)
        def q(*b):
            return orig(*(a + b))
        return curried(q, argc - len(a))
    
    func_name = getattr(orig, "__name__", getattr(orig, "__class__").__name__)
    wrapper.__name__ = func_name
    return wrapper