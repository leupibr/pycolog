"""Module for the `LogEntry` class"""
import re

import pycolog.plugins

NEW_LINE_CHAR = '\xB6'
"""Character to use instead of a new line while truncating."""


class LogEntry:
    """
    Represents a single log entry which may consists out of multiple lines.

    :param raw: The raw multiline string
    :type raw: str
    :param fields: Additional parsing settings of a field
    :type fields: dict
    :param line_format: Compiled regular expression for splitting the message into multiple fields.
    :type line_format: re.Pattern
    """
    def __init__(self, raw, **kwargs):
        self._options = kwargs
        self._raw = raw
        self._fields = kwargs.get('fields', {})
        self._line_format = kwargs.get('line_format', re.compile('^.*$'))

        match = self._line_format.match(raw)
        if match:
            self.attributes = self._parse_fields(match.groupdict())
        else:
            self.attributes = {}
        self.tags = set(self._find_tags())
        self._lines = self._raw.count('\n')
        self._interpreted = None

        pycolog.plugins.post_construct(self, self._options)

    @property
    def raw(self):
        return self._raw

    @property
    def interpreted(self):
        return self._interpreted

    @interpreted.setter
    def interpreted(self, value):
        self._interpreted = value

    def _parse_fields(self, attributes):
        return {k: self._parse_field(k, v) for k, v in attributes.items()}

    def _parse_field(self, field, value):
        setting = self._fields.get(field)
        if not setting:
            return value

        callback = setting.get('callback')
        kwargs = setting.get('kwargs', {})
        kwargs[setting['argument']] = value
        return callback(**kwargs)

    def _find_tags(self):
        for tag, config in self._options.get('tags', {}).items():
            match = config.get('pattern').search(self._raw)
            if not match:
                continue

            captures = match.groupdict()
            for capture, where in config.get('where', {}).items():
                if captures.get(capture, None) not in where.get('in', []):
                    break
            else:
                yield tag

    def __getattr__(self, item):
        return self.attributes.get(item)

    def __getitem__(self, item):
        return self.attributes.get(item)

    def __str__(self):
        return self._raw

    def interpreted_truncate(self, width):
        if not self._interpreted:
            return self.truncate(width)
        return self._truncate(self._interpreted, width)

    def truncate(self, width):
        """
        Returns a limited number of chars of the given line.
        If the line is too long, it will be truncated and ellipsis are appended.
        New lines will be replaced by a special char

        :param width: Max number of chars
        :type width: int
        :returns: A truncated string with a length less or equal to `width`
        :rtype: str
        """
        return self._truncate(self._raw, width)

    def _truncate(self, message, width):
        msg = message.replace('\n', NEW_LINE_CHAR)
        if len(msg) > width:
            return msg[:width - 3] + '...'
        return msg
