#!/usr/bin/env python
"""Start of the project"""

import sys
import argparse

import os.path as path

APP_PATH = path.abspath(path.join(path.dirname(__file__), path.pardir, 'app'))
sys.path.append(APP_PATH)
import password_manager as pm

def start():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", action="store_true",help='test mode')

    options = vars(parser.parse_args())

    empty_keys = [k for k,v in options.items() if v==None]
    for k in empty_keys:
        del options[k]

    """Start the program"""
    pm.bootstrap(options)
    pm.startApp()

if __name__ == '__main__':
    start()
