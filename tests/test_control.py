import sys
import unittest

import os.path as path

APP_PATH = path.abspath(path.join(path.dirname(__file__), path.pardir, 'app'))
sys.path.append(APP_PATH)
import test_data_manager as tdm

def my_suite():
    suite = unittest.TestSuite()
    result = unittest.TestResult()
    suite.addTest(unittest.makeSuite(tdm.TestDatabaseManagerWithFoundation))
    suite.addTest(unittest.makeSuite(tdm.TestDatabaseManagerNoFoundation))
    runner = unittest.TextTestRunner()
    print(runner.run(suite))

my_suite()
