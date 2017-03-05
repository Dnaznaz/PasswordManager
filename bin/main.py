#!/usr/bin/env python
"""Start of the project"""


import sys
import os.path as opath

APP_PATH = opath.abspath(opath.join(opath.dirname(__file__), opath.pardir, 'app'))
sys.path.append(APP_PATH)

def start():
    """Start the program"""
    pass

if __name__ == 'main':
    start()
