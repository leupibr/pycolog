#!/usr/bin/env python3
from setuptools import setup


def main():
    setup(use_scm_version={'write_to': "pycolog/_version.py"})


if __name__ == "__main__":
    main()

