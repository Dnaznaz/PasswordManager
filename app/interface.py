'''Inteface between all modules and allows command line inteface in test mode'''

from sys import platform
import threading

import communication as comm
import data_management as dm
import crypto_manager as crypto

_killEvent = threading.Event()

def init(**kwargs):
    '''Initiate the interface'''

    threading.Thread(target=comm.init, name='communication', daemon=True).start()

    if kwargs['cmdListening'] is True:
        threading.Thread(target=cmd_listener, name='CMD listener', args=(_killEvent,)).start()

    print('started interface')

def cmd_listener(event):
    '''Allows testing commands through the command line'''

    while not event.is_set():
        # get input from command line
        data = input('Enter command>>')

        # shuts down the program if the input was exit
        if data == "exit":
            shutdown()
            break

        caller(data)


def split_args(data, sep):
    '''Split a single string to key value pair dict by separator'''

    args = {}
    for arg in data:
        pair = arg.split(sep)
        if len(pair) == 1:
            print('key:{0} did not have any value'.format(pair[0]))
        elif pair[0] == '' or pair[0] == ' ':
            print('no key for value:{0}'.format(pair[1]))
        else:
            args[pair[0].upper] = pair[1]

    return args

def caller(raw_data):
    '''Calles commands to run'''

    args = split_args(raw_data.split(' '), '=')

    commandName = _pop_value(args, 'COMMAND')
    if commandName is None:
        print('no command was supplied')
    else:
        try:
            command = _commandsDict[commandName]
        except:
            print("no command named {}".format(commandName))

        threading.Thread(target=command, kwargs=args).start()

def get_password(**kwargs):
    '''DOC'''

    pID = _pop_value(kwargs, 'ID')
    reqID = _pop_value(kwargs, "REQ_ID")

    if reqID is None:
        print('no requestor ID supplied')
        return

    if pID is None:
        print('no ID was supplied')
        return

    encPass = dm.getPassFromDatabase(pID)

    if encPass is None:
        print('error retriving password, ID={0}'.format(pID))
        return

    auth_password = _pop_value(kwargs, 'AUTH_PASSWORD')
    if auth_password is None:
        print('no authorization password was supplied')
        return

    decPass = crypto.decrypt(auth_password, encPass)

    if decPass is None:
        print('error retriving password, ID={0}'.format(pID))
        return

    #TODO comm send password or error

def set_password(**kwargs):
    '''DOC'''

    name = _pop_value(kwargs, 'NAME')
    password = _pop_value(kwargs, 'PASSWORD')
    pID = _pop_value(kwargs, 'ID')
    reqID = _pop_value(kwargs, "REQ_ID")
    auth_password = _pop_value(kwargs, 'AUTH_PASSWORD')

    if reqID is None:
        print('no requestor ID supplied')
        return
    if pID is None:
        print('no ID was supplied')
        return
    if name is None:
        print('no name was supplied')
        return
    if password is None:
        print('no password was supplied')
        return
    if auth_password is None:
        print('no authorization password was supplied')
        return

    encName = crypto.encrypt(auth_password, name)
    encPass = crypto.encrypt(auth_password, password)

    if crypto.authorize(auth_password) is True:
        dm.setInDatabase(pID, encName, encPass)

    #TODO comm send OK or error

def delete_password(**kwargs):
    '''DOC'''

    pID = _pop_value(kwargs, 'ID')
    reqID = _pop_value(kwargs, "REQ_ID")
    auth_password = _pop_value(kwargs, 'AUTH_PASSWORD')

    if reqID is None:
        print('no requestor ID supplied')
        return
    if pID is None:
        print('no ID was supplied')
        return
    if auth_password is None:
        print('no authorization password was supplied')
        return

    if crypto.authorize(auth_password) is True:
        dm.deleteFromDatabase(pID)

    #TODO comm send OK or error

def get_data_list(**kwargs):
    '''DOC'''

    nameDict = {}

    reqID = _pop_value(kwargs, "REQ_ID")
    auth_password = _pop_value(kwargs, 'AUTH_PASSWORD')

    if reqID is None:
        print('no requestor ID supplied')
        return
    if auth_password is None:
        print('no authorization password was supplied')
        return

    if crypto.authorize(auth_password) is True:
        table = dm.getAllFromTable()
    else:
        return

    for pID, name, password in table:
        nameDict[pID] = crypto.decrypt(auth_password, name)

    #TODO comm send nameDict or error

_commandsDict = {
    "GET":get_password,
    "SET":set_password,
    "DELETE":delete_password,
    "GET-ALL":get_data_list
    }

def shutdown():
    '''Shuts down the program'''

    dm.closeConnection()
    _killEvent.set()

def _pop_value(dict, key):
    '''Return the value from the given key and the delete the entry'''

    try:
        return dict.pop(key)
    except:
        return None
