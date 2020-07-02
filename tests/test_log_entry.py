import pytest
import re

from pycolog.log_entry import LogEntry


@pytest.mark.parametrize('chars,expected', [
    (4, 'S...'),
    (8, 'Short...'),
    (9, 'ShortLine'),
    (12, 'ShortLine'),
])
def test_truncate(chars, expected):
    assert LogEntry('ShortLine').truncate(chars) == expected


def test_fields_as_attributes():
    subject = LogEntry(
        'Space separated log line',
        line_format=re.compile(r'^(?P<a>\w+)\s\w+\s(?P<b>\w+)\s(?P<c>\w+)'))

    assert subject.a == 'Space'
    assert subject.b == 'log'
    assert subject.c == 'line'


def test_fields_as_items():
    subject = LogEntry(
        'Space separated log line',
        line_format=re.compile(r'^(?P<a>\w+)\s\w+\s(?P<b>\w+)\s(?P<c>\w+)'))

    assert subject['a'] == 'Space'
    assert subject['b'] == 'log'
    assert subject['c'] == 'line'


def test_formatted_field():
    subject = LogEntry(
        'Space separated log line',
        line_format=re.compile(r'^(?P<a>\w+)\s\w+\s(?P<b>\w+)\s(?P<c>\w+)'),
        fields={'a': {'callback': lambda s: s[::-1], 'argument': 's'}}
    )
    assert subject.a == 'ecapS'


def test_formatted_field_additional_args():
    subject = LogEntry(
        'Space separated log line',
        line_format=re.compile(r'^\w+\s(?P<a>\w+)\s\w+\s\w+'),
        fields={'a': {
            'callback': lambda start, stop, step, value: value[start:stop:step],
            'kwargs': {'start': 1, 'stop': 6, 'step': 2},
            'argument': 'value'}
        }
    )
    assert subject.a == 'eaa'
