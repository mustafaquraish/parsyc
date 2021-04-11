class ParserResult:
    @staticmethod
    def reject():
        return ParserResult(None, None)    

    def __init__(self, rest, val=None):
        self.rest = rest
        self.ans = val

    def __bool__(self):
        return self.ans is not None

    def get(self):
        if self.ans is None:
            return None
        else:
            return self.ans

    def __repr__(self):
        if not self:
            return "Unable to parse"
        else:
            return f'Uncomsumed="{self.rest}", Answer={self.ans}'