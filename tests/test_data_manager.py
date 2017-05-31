import unittest
import os
import sqlite3

import data_management as dm

class TestDatabaseManagerWithFoundation(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.stockValues = [(50,'daniel','1234'),(1,'gal','5678')]
        dm.PASSWORDS_DATA_PATH = r'data\test.db'

        open(dm.PASSWORDS_DATA_PATH, 'x').close()

        self.conn = sqlite3.connect(dm.PASSWORDS_DATA_PATH)
        self.cursor = self.conn.cursor()

        self.cursor.execute('''CREATE TABLE PASSWORDS
        (ID INT PRIMARY KEY    NOT NULL,
        NAME        TEXT    NOT NULL,
        PASS        TEXT    NOT NULL);''')

        dm._initConnection()

    @classmethod
    def tearDownClass(self):
        self.conn.close()
        dm._closeConnection()
        os.remove(dm.PASSWORDS_DATA_PATH)

    def setUp(self):
        self.cursor.executemany("INSERT INTO PASSWORDS VALUES (?,?,?)", self.stockValues)
        self.conn.commit()

    def tearDown(self):
        self.cursor.execute("DELETE FROM PASSWORDS")
        self.conn.commit()

    def testCleanup(self):
        dm._cleanup()
        dm.saveChanges()

        self.cursor.execute("SELECT ID from PASSWORDS")

        data = self.cursor.fetchall()

        self.assertEqual(data[0][0], 0)
        self.assertEqual(data[1][0], 1)

    def testBigID(self):
        big = dm._getBigID()

        self.assertEqual(big, 50)

    def testGetAll(self):
        data = dm.getAllFromTable()

        self.assertListEqual(data, self.stockValues)

class TestDatabaseManagerNoFoundation(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        dm.PASSWORDS_DATA_PATH = r'data\test.db'

        open(dm.PASSWORDS_DATA_PATH, 'x').close()

        self.conn = sqlite3.connect(dm.PASSWORDS_DATA_PATH)
        self.cursor = self.conn.cursor()

        dm._initConnection()

    @classmethod
    def tearDownClass(self):
        self.conn.close()
        dm._closeConnection()
        os.remove(dm.PASSWORDS_DATA_PATH)

    def tearDown(self):
        self.cursor.execute("DROP TABLE IF EXISTS PASSWORDS")

    def testInitTable(self):
        dm._initTable()

        self.cursor.execute("SELECT * from PASSWORDS")
        names = list(map(lambda x: x[0], self.cursor.description))

        self.assertEqual(names[0], 'ID')
        self.assertEqual(names[1], 'NAME')
        self.assertEqual(names[2], 'PASS')

    def testInitDatabase(self):
        dm.initDatabase()
