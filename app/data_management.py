import sqlite3
import os

PASSWORDS_DATA_PATH = r'data\passwords.db'
_conn = None
_cursor = None
_maxID = 0

def _cleanup():
    '''Reorganizes the row id's to pack them more tightly'''
    _cursor.execute("SELECT ID FROM PASSWORDS")

    data = _cursor.fetchall()
    unorganized = []
    for i in range(len(data)):
        if data[i][0] != i:
            unorganized.append((i, data[i][0],))

    _cursor.executemany("UPDATE PASSWORDS set ID=? where ID=?", unorganized)

def _getBigID():
    '''Return the highest ID value in the table'''
    _cursor.execute("SELECT ID from PASSWORDS")
    ids = list(map(lambda x: x[0], _cursor.fetchall()))
    if len(ids) > 0:
        return max(ids)
    else:
        return 0

def _closeConnection():
    '''Close the connection to the table'''
    global _conn, _cursor

    if _cursor is not None:
        _cursor.close()
        _cursor = None
    if _conn is not None:
        _conn.close()
        _conn = None

def _setConnection(connection):
    global _conn

    if _conn is not None:
        _conn.close()
        _conn = None
    _conn = connection

def _setCursor(cur):
    global _cursor

    if _cursor is not None:
        _cursor.close()
        _cursor = None
    _cursor = cur

def _initConnection():
    '''Start the connection to the table'''
    _setConnection(sqlite3.connect(PASSWORDS_DATA_PATH))
    _setCursor(_conn.cursor())

    print('opened database connection')

def _initTable():
    '''Open a new table in the database'''
    if _conn is None or _cursor is None:
        _initConnection()

    _cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='PASSWORDS'")
    if _cursor.fetchone() is None:
        _cursor.execute('''CREATE TABLE PASSWORDS
        (ID INT PRIMARY KEY    NOT NULL,
        NAME        TEXT    NOT NULL,
        PASS        TEXT    NOT NULL);''')
    print('init table')

def initDatabase():
    if not os.path.isfile(PASSWORDS_DATA_PATH):
        createDatabase()
    else:
        _initTable()
    print("finished database init")

    global _maxID
    _maxID = _getBigID()

def createDatabase():
    open(PASSWORDS_DATA_PATH, 'x').close()
    print('created new database')
    _initTable()

def getAllFromTable():
    _cursor.execute("SELECT id, name, pass from PASSWORDS")

    return list(map(lambda x: (x[0], x[1], x[2]), _cursor.fetchall()))

def getPassFromDatabase(key):
    val = (key,)

    _cursor.execute("SELECT pass from PASSWORDS where ID=?", val)
    return _cursor.fetchone()

def addToDatabase(name, value):
    val = (_maxID, name, value,)
    _conn.execute("INSERT INTO PASSWORDS (ID,NAME,PASS) VALUES (?,?,?)", val)

def changeInDatabase(ID, name, value):
    val = (ID, name, value,)
    _conn.execute("UPDATE PASSWORDS set NAME = ?, PASS = ? where ID=?", val)

def deleteFromDatabase(ID):
    val = (ID,)
    _conn.execute("DELETE from PASSWORDS where ID=?", val)

def makeBackup(file):
    n = 1
    while (os.path.isfile('data\passwords{}.db.old'.format(n))):
        n += 1

    fileName = 'data\passwords{}.db.old'.format(n)

    open(fileName, 'x').close()
    with open(fileName, 'w') as backupFile:
        for line in file.readlines():
            backupFile.write(line)

    return fileName

def cancelChanges():
    _conn.rollback()

def saveChanges():
    _conn.commit()

def closeConnection():
    _cleanup()
    saveChanges()
    _closeConnection()
