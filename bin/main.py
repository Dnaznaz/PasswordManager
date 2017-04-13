#!/usr/bin/env python
"""Start of the project"""

import sys
import os.path as path

APP_PATH = path.abspath(path.join(path.dirname(__file__), path.pardir, 'app'))
sys.path.append(APP_PATH)
import password_manager as pm

def start():
    """Start the program"""
    pm.bootstrap()
    pm.startApp()

if __name__ == 'main':
    start()
