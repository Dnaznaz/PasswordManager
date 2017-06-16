#!/usr/bin/env python3
"""The start of the project"""

import sys
import argparse

import os.path as path

# adds the app modules to the system path
APP_PATH = path.abspath(path.join(path.dirname(__file__), path.pardir, 'app'))
sys.path.append(APP_PATH)
import password_manager as pm

def start():
    "starts up the program and its requirements"

    # allowes to run the program with spacial arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", action="store_true", help='test mode')
    parser.add_argument("-r", "--reset", action="store_true", help='reset database')
    parser.add_argument("--nonet", action="store_true", help="disable networking")

    options = vars(parser.parse_args())

    empty_keys = [k for k, v in options.items() if v is None]
    for k in empty_keys:
        del options[k]

    pm.bootstrap(options)
    pm.start_app()

if __name__ == '__main__':
    start()
