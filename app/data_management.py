import sqlite3
import os
import time
import binascii
import threading

DATABASE_PATH = None
_conn = None
_sqlWorker = None
_requests = {}
_answers = {}
rID = 0

def _init_worker():
    _init_table()

    print("finished database init")

    on = True

    global _conn
    while on:
        if bool(_requests):
            cur = _conn.cursor()
            ID, req = _requests.popitem()

            if req == "CLOSE":
                on = False

                if _conn is not None:
                    _conn.close()
                    _conn = None
            else:
                cur.execute(req[0], req[1])
                _conn.commit()

                _answers[ID] = cur.fetchall()

def _set_connection(connection):
    '''DOC'''

    global _conn

    if _conn is not None:
        _conn.close()
        _conn = None
    _conn = connection

def _init_connection():
    '''Start the connection to the table'''

    _set_connection(sqlite3.connect(DATABASE_PATH))

    print('opened database connection')

def _init_table():
    '''Open a new table in the database'''

    if _conn is None:
        _init_connection()

    cur = _conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='PASSWORDS'") #TODO test if real none
    if cur.fetchone() is None:
        cur.execute('''CREATE TABLE PASSWORDS
        (ID INT PRIMARY KEY    NOT NULL,
        NAME        TEXT    NOT NULL,
        PASS        TEXT    NOT NULL,
        IV          TEST    NOT NULL);''')
    print('init table')

def init_database():
    '''DOC'''

    if not os.path.isfile(DATABASE_PATH):
        create_database()

    _sqlWorker = threading.Thread(target=_init_worker, daemon=True)
    _sqlWorker.start()

def create_database():
    '''DOC'''

    open(DATABASE_PATH, 'x').close()
    print('created new database')

def get_all_from_table():
    '''DOC'''

    global rID
    ID = rID
    rID =+ 1
    _requests[ID] = ("SELECT ID, NAME, PASS, IV from PASSWORDS", ())

    while ID not in _answers:
        pass
    res = _answers.pop(ID)

    l = list(map(lambda x: (x[0], x[1], x[2], binascii.unhexlify(x[3])), res))
    return l

def get_pass_from_database(key):
    '''DOC'''

    val = (key,)
    global rID
    ID = rID
    rID =+ 1
    _requests[ID] = ("SELECT NAME, PASS, IV from PASSWORDS where ID=?", val)

    while ID not in _answers:
        pass
    res = _answers.pop(ID)
    if len(res) > 0:
        res = res[0]
    else:
        return None

    if res:
        return (res[0], res[1], binascii.unhexlify(res[2]))
    else:
        return None

def set_in_database(rpID, name, value, iv):
    '''DOC'''

    global rID
    ID = rID
    rID =+ 1

    if type(rpID) == str:
        pID = int(rpID)
    elif type(rpID) == int:
        pID = rpID
    else:
        return -1

    if pID == -1:
        _requests[ID] = ("SELECT MAX(ID) FROM PASSWORDS", ())

        while ID not in _answers:
            pass
        newID = _answers.pop(ID)[0][0]
        if newID is None:
            newID = 1
        else:
            newID += 1

        val = (newID, name, value, binascii.hexlify(iv),)
        _requests[ID] = ("INSERT INTO PASSWORDS (ID,NAME,PASS,IV) VALUES (?,?,?,?)", val)

        while ID not in _answers:
            pass
        _answers.pop(ID)

        return newID
    else:
        _requests[ID] = ("SELECT COUNT(*) FROM PASSWORDS WHERE ID = ?", (pID,))

        while ID not in _answers:
            pass
        c = _answers.pop(ID)[0][0]

        if c == 0:
            return -1

        val = (name, value, binascii.hexlify(iv), pID,)
        _requests[ID] = ("UPDATE PASSWORDS set NAME = ?, PASS = ?, IV = ? where ID=?", val)

        while ID not in _answers:
            pass
        _answers.pop(ID)

        return pID

def delete_from_database(pID):
    '''DOC'''

    global rID
    ID = rID
    rID =+ 1

    _requests[ID] = ("SELECT COUNT(*) FROM PASSWORDS WHERE ID = ?", (pID,))

    while ID not in _answers:
        pass
    c = _answers.pop(ID)[0][0]

    if c == 0:
        return False

    val = (pID,)
    _requests[ID] = ("DELETE from PASSWORDS where ID=?", val)

    return True

def make_backup(file):
    '''DOC'''

    fileName = 'data/passwords{month}.{day}.{year}.{hour}.{minute}.db.old'.format(
        day=time.strftime('%d'),
        month=time.strftime('%h'),
        year=time.strftime('%y'),
        hour=time.strftime('%H'),
        minute=time.strftime('%M')
        )

    open(fileName, 'x').close()
    with open(fileName, 'w') as backupFile:
        for line in file.readlines():
            backupFile.write(line)

    return fileName

def close_connection():
    '''Close the connection to the table'''

    _requests[0] = "CLOSE"

def shutdown():
    close_connection()
