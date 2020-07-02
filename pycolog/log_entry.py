"""Module for the `LogEntry` class"""
import re

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
        self._lines = self._raw.count('\n')

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

    def __getattr__(self, item):
        return self.attributes.get(item)

    def __getitem__(self, item):
        return self.attributes.get(item)

    def __str__(self):
        return self._raw

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
        msg = self._raw.replace('\n', NEW_LINE_CHAR)
        if len(msg) > width:
            return msg[:width - 3] + '...'
        return msg
