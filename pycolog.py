#!/usr/bin/env python3
import argparse
import pathlib

import yaml

from pycolog import yaml_loader
from pycolog.log import Log
from pycolog.screens import LogScreen

yaml_loader.register()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--layout', type=pathlib.Path, required=True, help='Path to the logs layout definition file')
    parser.add_argument('files', type=pathlib.Path, nargs='+', metavar='file',
                        help='Path to the log files to be analyzed')

    parser.add_argument('--color-screen', action='store_true',
                        help='Show a color overview screen before starting the default routines')

    config = parser.parse_args().__dict__
    with open(config.get('layout')) as f:
        config.update(yaml.safe_load(f))

    analyzer = Log(**config)
    with LogScreen(analyzer, **config) as screen:
        screen.run()
