import sqlite3
import os
import time

DATABASE_PATH = None
_conn = None

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
        PASS        TEXT    NOT NULL);''')
    print('init table')

def init_database():
    '''DOC'''

    if not os.path.isfile(DATABASE_PATH):
        create_database()

    _init_table()
    print("finished database init")

def create_database():
    '''DOC'''

    open(DATABASE_PATH, 'x').close()
    print('created new database')

def get_all_from_table():
    '''DOC'''

    cur = _conn.cursor()
    cur.execute("SELECT ID, NAME, PASS from PASSWORDS")

    return list(map(lambda x: (x[0], x[1], x[2]), cur.fetchall()))

def get_pass_from_database(key):
    '''DOC'''

    val = (key,)

    cur = _conn.cursor()
    cur.execute("SELECT pass from PASSWORDS where ID=?", val)

    res = cur.fetchone()
    if res:
        return res[0]
    else:
        return None

def set_in_database(ID, name, value):
    '''DOC'''

    checkVal = (ID,)

    cur = _conn.cursor()
    count = cur.execute("select count(1) from PASSWORDS where ID = ?", checkVal).fetchone()[0]

    val = (ID, name, value,)
    try:
        if count == 0:
            cur.execute("INSERT INTO PASSWORDS (ID,NAME,PASS) VALUES (?,?,?)", val)
        else:
            cur.execute("UPDATE PASSWORDS set NAME = ?, PASS = ? where ID=?", val)
        _conn.commit()
        return True
    except:
        return False

def delete_from_database(ID):
    '''DOC'''

    val = (ID,)

    cur = _conn.cursor()
    try:
        cur.execute("DELETE from PASSWORDS where ID=?", val).rowcount
        _conn.commit()
        return True
    except:
        return False

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

    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None

def shutdown():
    close_connection()
