

new_line_char = '\xB6'


class LogEntry:
    def __init__(self, raw, **kwargs):
        self._options = kwargs
        self._raw = raw
        self._fields = kwargs.get('fields', {})
        self._line_format = kwargs.get('line_format')

        m = self._line_format.match(raw)
        if m:
            self.attributes = self._parse_fields(m.groupdict())
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
        kwargs = setting.get('kwargs')
        kwargs[setting['argument']] = value
        return callback(**kwargs)

    def __getattr__(self, item):
        return self.attributes.get(item)

    def __getitem__(self, item):
        return self.attributes.get(item)

    def __str__(self):
        return self._raw

    def truncate(self, width):
        msg = self._raw.replace('\n', new_line_char)
        if len(msg) > width:
            return msg[:width - 3] + '...'
        return msg
