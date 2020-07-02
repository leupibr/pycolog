import yaml
import datetime
import pycolog.yaml_loader


def test_strptime_registration():
    pycolog.yaml_loader.register()
    content = yaml.safe_load("timestamp: !!python/strptime")

    parsed = content['timestamp']('2 July, 2020', '%d %B, %Y')
    expected = datetime.datetime(2020, 7, 2, 0, 0)
    assert parsed == expected


def test_regexp_registration():
    content = yaml.safe_load("regexp: !!python/regexp '^A.*$'")
    assert content['regexp'].match('ABC')
    assert not content['regexp'].match('BCD')
