import re
from datetime import datetime

import yaml


def strptime(date_string, format):
    """
    Wrapper around :meth:`datetime.strptime` which allows to pass keyword arguments

    .. seealso:: :meth:`datetime.strptime`

    :param date_string: Input date to parse
    :type date_string: str
    :param format: Format of the input string
    :type format: str
    :returns: New :class:`datetime.datetime` parsed from the given `date_string`
    :rtype: datetime
    """
    return datetime.strptime(date_string, format)


def register():
    """
    Registers well certain constructors used for the :class:`yaml.SafeLoader`.
    """
    yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:python/regexp', lambda l, n: re.compile(l.construct_scalar(n)))
    yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:python/strptime', lambda l, n: strptime)
