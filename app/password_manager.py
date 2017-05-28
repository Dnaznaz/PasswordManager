import os

import data_management as dm
import interface

def bootstrap():
    if not os.path.exists('log'):
        os.makedirs('log')

    if not os.path.exists('tmp'):
        os.makedirs('tmp')

    if not os.path.exists('data'):
        os.makedirs('data')

    create_pid()

def create_pid():
    f = open('tmp/tracks.pid', 'w')
    f.write("{0}".format(os.getpid()))
    f.close()

def startApp():
    with dm.DatabaseManager() as dbm:
        inter = interface.Interface()
