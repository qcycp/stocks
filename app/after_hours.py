class AfterHoursInfo:
    def __init__(self, code, name, volume, open, high, low, close):
        self.code = str(code)
        self.name = str(name)
        self.volume = int(volume)
        self.open = float(open) if open.isdigit() else open
        self.high = float(high) if high.isdigit() else high
        self.low = float(low) if low.isdigit() else low
        self.close = float(close) if close.isdigit() else close

    def __repr__(self):
        return 'code({}), name({}), open({}), high({}), low({}), close({}), volume({})'.format(
            self.code, self.name, self.open, self.high, self.low, self.close, self.volume)