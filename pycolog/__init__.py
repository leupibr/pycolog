"""
Small console application that allows quick analyzation of log files
"""
import argparse
import pathlib

import yaml

from pycolog import yaml_loader
from pycolog.log import Log
from pycolog.screens import LogScreen
from pycolog.plugins import load as load_plugins, mount as mount_plugins

try:
    from pycolog.version import version as __version__
except ImportError:
    __version__ = '0.0.0'


def console_main():
    """Main entry point if executing `pycoloc`"""
    yaml_loader.register()

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=f'{__version__}')

    parser.add_argument('files', type=pathlib.Path, nargs='+', metavar='file',
                        help='Path to the log files to be analyzed')

    parser.add_argument('--layout', type=pathlib.Path, required=True, help='Path to the logs layout definition file')
    parser.add_argument('--color-screen', action='store_true',
                        help='Show a color overview screen before starting the default routines')

    config = parser.parse_args().__dict__
    with open(config.get('layout')) as layout:
        config.update(yaml.safe_load(layout))

    config['plugins'] = list(load_plugins(config.get('plugins', [])))
    mount_plugins(config)

    analyzer = Log(**config)
    with LogScreen(analyzer, **config) as screen:
        screen.run()


if __name__ == '__main__':
    console_main()
