#!/usr/bin/env python3
"""
Packaging file executing the `setuptools.setup` function.
The setup is heavily relying on the `setup.cfg`, please check
this file for the pack settings.
"""
from setuptools import setup


def main():
    """
    Main method which is invoked when running this file
    """
    setup(use_scm_version={'write_to': "pycolog/version.py"})


if __name__ == "__main__":
    main()
