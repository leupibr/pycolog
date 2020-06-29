from glob import glob
from re import split, compile

from pycolog.log_entry import LogEntry


def _expand_file_paths(file_paths):
    for file_path in file_paths:
        yield from glob(str(file_path))


def _natural_sort(files):
    return sorted(files, key=lambda key: [int(c) if c.isdigit() else c.lower() for c in split('([0-9]+)', key)])


class Log:
    def __init__(self, **kwargs):
        self._options = kwargs

        self._entry_start = kwargs.get('line_start', compile(r'^'))

        self._raw_lines = []
        files = _expand_file_paths(kwargs.get('files'))
        for file in _natural_sort(files):
            with open(file) as f:
                self._raw_lines.extend(f.readlines())

        self._entries = list(self._find_entries())
        self._total = len(self._entries)

    @property
    def total(self):
        return self._total

    def get_entries(self, slice_):
        return self._entries[slice_]

    def get_entry(self, idx):
        return self._entries[idx]

    def _find_entries(self):
        first = True
        current = ''

        for raw in self._raw_lines:
            if not self._entry_start.match(raw):
                current += raw
                continue

            if not first:
                yield LogEntry(current.strip(), **self._options)
            first = False
            current = raw
        yield LogEntry(current.strip(), **self._options)
