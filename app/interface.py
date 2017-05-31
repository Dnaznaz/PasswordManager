from sys import platform
import threading

import communication as comm
import data_management as dm

def init():
    if platform == 'linux' or platform == 'linux2':
        comm.init()

    t = threading.Thread(target=cmdListener)
    t.start()

    print('start interface')

def cmdListener():
    import password_manager as pm

    while pm.getIsRunning:# is True: #Debug
        data = input().split(' ')
        if len(data) > 1:
            commandName = data.pop(0)
            args = {}
            try:
                for arg in data:
                    key, value = arg.split('=')
                    args[key.upper] = value
            except:
                print('one or more arguments did not have any value')
                args = None
        else:
            commandName = data[0]
            args = {}

        if commandName == "exit":
            pm.setIsRunning(False)
        else:
            command = None
            try:
                command = _commandsDict[commandName]
            except:
                print("no command named {}".format(commandName))
            if command is not None and args is not None:
                threading.Thread(target=command, kwargs=args).start()

def getPassword(**kwargs):
    args = {'ID':None}
    isRun = True

    for argName in args:
        try:
            args[argName] = kwargs[argName.upper]
        except:
            isRun = False
            print('the argument {} is missing'.format(argName))

    if isRun is True:
        return dm.getPassFromDatabase(args['ID'])

def setPassword(**kwargs):
    args = {
        'NAME':None,
        'PASSWORD':None
        }
    isRun = True

    for argName in args:
        try:
            args[argName] = kwargs[argName]
        except:
            isRun = False
            print('the argument {} is missing'.format(argName))

    if isRun is True:
        dm.addToDatabase(args['NAME'], args['PASSWORD'])

def updatePassword(**kwargs):
    args = {
        'ID':None,
        'NAME':None,
        'PASSWORD':None
        }
    isRun = True

    for argName in args:
        try:
            args[argName] = kwargs[argName]
        except:
            isRun = False
            print('the argument {} is missing'.format(argName))

    if isRun is True:
        dm.addToDatabase(args['ID'], args['NAME'], args['PASSWORD'])

def deletePassword(**kwargs):
    args = {'ID':None}
    isRun = True

    for argName in args:
        try:
            args[argName] = kwargs[argName]
        except:
            isRun = False
            print('the argument {} is missing'.format(argName))

    if isRun is True:
        dm.addToDatabase(args['ID'])

def getDataList(**kwargs):
    return list(map(lambda x: (x[0], x[1]), dm.getAllFromTable()))

_commandsDict = {
    "GET":getPassword,
    "INSERT":setPassword,
    "CHANGE":updatePassword,
    "DELETE":deletePassword,
    "GET-ALL":getDataList
    }
