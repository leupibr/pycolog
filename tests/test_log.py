from pycolog.log import Log


def test_natural_sort(tmp_path):
    a = tmp_path / 'file_2.log'
    a.write_text('A\nB')
    b = tmp_path / 'file_03.log'
    b.write_text('C')
    c = tmp_path / 'file_10.log'
    c.write_text('D')

    log = Log(files=[c, b, a])
    assert log._raw_lines == ['A\n', 'B', 'C', 'D']


