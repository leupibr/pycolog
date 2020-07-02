import itertools

import pytest
import re

from pycolog.log import Log


@pytest.mark.parametrize('order', itertools.permutations(range(3)))
def test_natural_sort(tmp_path, order):
    files = [
        tmp_path / 'file_2.log',
        tmp_path / 'file_03.log',
        tmp_path / 'file_10.log',
    ]

    files[0].write_text('A\nB')
    files[1].write_text('C')
    files[2].write_text('D')

    log = Log(files=[files[i] for i in order])
    assert log._raw_lines == ['A\n', 'B', 'C', 'D']


@pytest.mark.parametrize('content,expected', [('A', 1), ('A\nB', 2), ('A\nB\n', 2)])
def test_total(tmp_path, content, expected):
    f = tmp_path / 'input.log'
    f.write_text(content)
    assert Log(files=[f]).total == expected


@pytest.mark.parametrize('content,expected', [
    ('A', 1), ('A\nBA\n', 1), ('A\nA\nAB', 3)
])
def test_total_pattern(tmp_path, content, expected):
    f = tmp_path / 'input.log'
    f.write_text(content)
    assert Log(files=[f], line_start=re.compile('^A')).total == expected


def test_get_entries(tmp_path):
    f = tmp_path / 'input.log'
    f.write_text('''not
    the best
    log
    file''')

    assert [str(l) for l in Log(files=[f]).get_entries(slice(1, 3))] == ['the best', 'log']

def test_get_entry(tmp_path):
    f = tmp_path / 'input.log'
    f.write_text('''not
    the best
    log
    file''')

    assert str(Log(files=[f]).get_entry(2)) == 'log'
