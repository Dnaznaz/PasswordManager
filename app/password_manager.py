import os
import atexit
import threading

import data_management as dm
import interface

RUNNING = True
runningLock = threading.Lock()

def getIsRunning():
    value = False

    runningLock.acquire()
    try:
        value = RUNNING
    finally:
        runningLock.release()

    return value

def setIsRunning(value):
    global RUNNING

    runningLock.acquire()
    try:
        RUNNING = value
    finally:
        runningLock.release()

def bootstrap(options):
    if not os.path.exists('log'):
        os.makedirs('log')

    if not os.path.exists('tmp'):
        os.makedirs('tmp')

    if not os.path.exists('data'):
        os.makedirs('data')

    create_pid()
    atexit.register(delete_pid)
    atexit.register(dm.closeConnection)

    if options['test'] is True and os.path.isfile(dm.PASSWORDS_DATA_PATH):
        os.remove(dm.PASSWORDS_DATA_PATH)

    dm.initDatabase()

def create_pid():
    f = open('tmp/tracks.pid', 'w')
    f.write("{0}".format(os.getpid()))
    f.close()

def delete_pid():
    os.remove('tmp/tracks.pid')

def startApp():
    interface.init()
