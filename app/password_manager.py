'''Implementation of the methods that start the program and its requirements'''

import logging
import time
import sys
import os
import json
import atexit

import data_management as dm
import crypto_manager as crypto
import interface

config = {}
logger = None

def bootstrap(options):
    '''Setup needed requirements'''

    # place to save logging data
    if not os.path.exists('log'):
        os.makedirs('log')

    # place to save temporary data
    if not os.path.exists('tmp'):
        os.makedirs('tmp')

    # place to save database
    if not os.path.exists('data'):
        os.makedirs('data')

    create_pid()
    init_config(options)
    init_logger()

    logger.info('Starting app on pid: {0}'.format(os.getpid()))
    logger.debug('With config:')
    logger.debug(config)

    # add commands to activate at program shutdown
    atexit.register(interface.shutdown)
    atexit.register(delete_pid)

    dm.DATABASE_PATH = config['database_path']
    crypto.MASTER_PASSWORD = config['master_password']
    crypto.SALT = config['salt']

    # delete existent database if in reset arg was given
    if config['reset'] is True and os.path.isfile(dm.DATABASE_PATH):
        os.remove(dm.DATABASE_PATH)

    dm.init_database()

def create_pid():
    '''Save the pid number of the proccess in "tmp/pid"'''

    f = open('tmp/tracks.pid', 'w')
    f.write("{0}".format(os.getpid()))
    f.close()

def delete_pid():
    '''Delete the proccess pid at program shutdown'''

    os.remove('tmp/tracks.pid')

def init_config(options):
    path = None

    with open('config/config.json') as data_file:
        cfg = json.load(data_file)
        global config

        config = dict(cfg['default'], **options)

def init_logger():
    '''Start a logger'''

    logging.basicConfig(
        filename='log/{month}.{day}.{year}.{hour}.{minute}.log'.format(
            day=time.strftime('%d'),
            month=time.strftime('%h'),
            year=time.strftime('%y'),
            hour=time.strftime('%H'),
            minute=time.strftime('%M')
            ),
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s'
        )
    logging.captureWarnings(True)
    root = logging.getLogger()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    global logger
    logger = logging

def start_app():
    '''Start the interface of the program'''

    interface.init_interface(cmdListening=config['test'])
