"""Module for `Log`"""
from glob import glob
import re

from pycolog.log_entry import LogEntry


def _expand_file_paths(file_paths):
    for file_path in file_paths:
        yield from glob(str(file_path))


def _natural_sort(files):
    return sorted(files, key=lambda key: [int(c) if c.isdigit() else c.lower() for c in re.split('([0-9]+)', key)])


class Log:
    """
    The log class splits up the concatenated content of the input files (`files`)
    into multiple messages that can be retrieved by an index or slice later.

    :param files: List of paths to the log files
    :type file: list[str]
    :param line_start: Compiled regular expression containing the line start pattern.
    :type line_start: re.Pattern
    """
    def __init__(self, **kwargs):
        self._options = kwargs

        self._entry_start = kwargs.get('line_start', re.compile(r'^'))

        self._raw_lines = []
        files = _expand_file_paths(kwargs.get('files'))
        for file_path in _natural_sort(files):
            with open(file_path) as file_handle:
                self._raw_lines.extend(file_handle.readlines())

        self._entries = list(self._find_entries())
        self._total = len(self._entries)

    @property
    def total(self):
        """Gets the total count of messages. This may differs to the total count of lines."""
        return self._total

    def get_entries(self, slice_):
        """Get multiple entries given by a slice."""
        return self._entries[slice_]

    def get_entry(self, idx):
        """Get one specific entry."""
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
