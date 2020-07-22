"""Module for the environment holder class"""


class Environment:
    """The contains the settings and formats actual screen state"""
    def __init__(self):
        super(Environment, self).__setattr__('_environment', dict())

    @property
    def line_format(self):
        """
        Returns the log line format.

        :return: format-able string for
            * 0: index
            * 1: message
        :rtype: str
        """
        return f'{{:{self.idxlen}d}}: {{:.{self.msglen}s}}'

    @property
    def status_format(self):
        """
        Returns the status line format

        :return: format-able string with
            * 0: start line
            * 1: end line
            * 2: total lines
        :rtype: str
        """
        return '{} .. {} / {}{}'

    def __getitem__(self, item):
        return self._environment[item]

    def __setitem__(self, key, value):
        self._environment[key] = value

    def __getattr__(self, item):
        return self._environment[item]

    def __setattr__(self, key, value):
        self._environment[key] = value
