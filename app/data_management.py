import sqlite3
import os

PASSWORDS_DATA_PATH = 'data\passwords.db'

class DatabaseManager:

    def __init__(self):
        if not os.path.isfile(PASSWORDS_DATA_PATH):
            self.createDatabase()
        else:
            self.conn = sqlite3.connect(PASSWORDS_DATA_PATH)
        print('opened database connection')

        self.maxID = self._getBigID()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.closeConnection()

    def _execute(self, command, values=None):
        if values is not None:
            return self.conn.execute(command, values)
        else:
            return self.conn.execute(command)

    def _cleanup(self):
        data = self.getAllFromTable()

        for i in range(len(data)):
            if data[i][0] != i:
                val = (i, data[i][0],)
                self._execute("UPDATE PASSWORDS set ID=? where ID=?", val)

    def _getBigID(self):
        for row in self._execute("SELECT Count(*) from PASSWORDS"):
            return row[0]

    def createDatabase(self):
        open(PASSWORDS_DATA_PATH, 'x').close()

        self.conn = sqlite3.connect(PASSWORDS_DATA_PATH)
        self._execute('''CREATE TABLE PASSWORDS
        (ID INT PRIMARY KEY    NOT NULL,
        NAME        TEXT    NOT NULL,
        PASS        TEXT    NOT NULL);''')
        print('created new table')

    def getPassFromDatabase(self, key):
        val = (key,)
        for row in self._execute("SELECT pass from PASSWORDS where ID=?", val):
            return row[0]

    def getAllFromTable(self):
        data = []
        cursor = self._execute("SELECT id, name, pass from PASSWORDS")

        for row in cursor:
            data.append((row[0], row[1], row[2]))

        return data

    def addToDatabase(self, name, value):
        val = (self.maxID, name, value,)
        self._execute("INSERT INTO PASSWORDS (ID,NAME,PASS) VALUES (?,?,?)", val)

    def changeInDatabase(self, ID, name, value):
        val = (ID, name, value,)
        self._execute("UPDATE PASSWORDS set NAME = ?, PASS = ? where ID=?", val)

    def deleteFromDatabase(self, ID):
        val = (ID,)
        self._execute("DELETE from PASSWORDS where ID=?", val)

    def makeBackup(self, file):
        n = 1
        while (os.path.isfile('data\passwords{}.db.old'.format(n))):
            n += 1

        fileName = 'data\passwords{}.db.old'.format(n)

        open(fileName, 'x').close()
        with open(fileName, 'w') as backupFile:
            for line in file.readlines():
                backupFile.write(line)

        return fileName

    def cancelChanges(self):
        self.conn.rollback()

    def saveChanges(self):
        self.conn.commit()

    def closeConnection(self):
        self._cleanup()
        self.saveChanges()
        self.conn.close()
