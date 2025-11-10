#!/usr/bin/env python3
"""main module"""
import sys

from metripy.Application.Application import Application


def main():
    """cli entry point to application"""
    application = Application()
    application.run(sys.argv)


if __name__ == "__main__":
    main()
