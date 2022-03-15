from cello_mvc.CelloDB import CelloDB
import sqlite3
import os
import time

import unittest

class TestDB(unittest.TestCase):
    def test_a_new_database(self):
        try:
            os.remove("test/integration/fixtures/test_a.db")
        except:
            pass
        db = CelloDB("test/integration/fixtures/test_a.db")
        db.new_database()
        """
        Test that the file is not empty.
        """
        db_file_size = os.path.getsize("test/integration/fixtures/test_a.db")
        self.assertGreater(db_file_size, 0, "Database file is empty.")

    def test_b_insert_into_x_values_y(self):

        db = CelloDB("test/integration/fixtures/test_b.db")

        table = "user"
        user_name = time.localtime()
        user_address = time.localtime()

        db.insert_into_x_values_y(f'{table}', f'("{user_name}"), ("{user_address}")')

        con = sqlite3.connect("test/integration/fixtures/test_b.db")
        cur = con.cursor()

        result = cur.execute(f'SELECT * FROM {table}').fetchall()[-1]
        self.assertEqual((f'{user_name}', f'{user_address}'), result, "Values not inserted into database.")

        cur.close()
        con.close()
    
    def test_c_select_x_from_y_where_z(self):

        db = CelloDB("test/integration/fixtures/test_c.db")

        result = db.select_x_from_y_where_z("user_name", "user", "user_address = 'test_address'")[0]
        expected = ("test_user",)

        self.assertEqual(expected, result, "values not retrieved from database.")