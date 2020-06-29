
class Environment:
    def __init__(self):
        super(Environment, self).__setattr__('_environment', dict())

    @property
    def line_format(self):
        return f'{{:{self.idxlen}d}}: {{:.{self.msglen}s}}'

    @property
    def status_format(self):
        return '{} .. {} / {}'

    def __getitem__(self, item):
        return self._environment[item]

    def __setitem__(self, key, value):
        self._environment[key] = value

    def __getattr__(self, item):
        return self._environment[item]

    def __setattr__(self, key, value):
        self._environment[key] = value
