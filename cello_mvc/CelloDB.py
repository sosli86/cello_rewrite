import sqlite3
import sys
import traceback


def sqlite_error(er):
    print('****SQLite error: %s' % (' '.join(er.args)))
    print("Exception class is: ", er.__class__)
    print('SQLite traceback: ')
    exc_type, exc_value, exc_tb = sys.exc_info()
    print(traceback.format_exception(exc_type, exc_value, exc_tb))


class CelloDB(object):

    def __init__(self, path):
        self.path = path

    def new_database(self):
        self.con = sqlite3.connect(self.path)
        self.cur = self.con.cursor()
        print("Creating new database")
        try:
            self.cur.execute(
                "CREATE TABLE user ( \
                    user_name varchar, \
                    user_address varchar \
                )"
            )
            self.cur.execute(
                "CREATE TABLE contract (\
                    contract_address varchar, \
                    contract_name varchar \
                )"
            )
            self.cur.execute(
                "CREATE TABLE membership (\
                    user_name varchar, \
                    contract_name varchar, \
                    user_pub_key varchar, \
                    user_key_cipher varchar \
                    )"
            )
            self.cur.execute(
                "CREATE TABLE message ( \
                    contract_name varchar, \
                    contents varchar \
                )"
            )
            self.con.commit()
            
        except sqlite3.Error as er:
            print(sqlite_error(er))
        
        self.cur.close()
        self.con.close()

    def select_x_from_y_where_z(self, x, y, z=""):
        self.con = sqlite3.connect(self.path)
        self.cur = self.con.cursor()
        try:
            if z != "":
#                print(f'select { x } from { y } where { z }')
                result = self.cur.execute(
                    f'SELECT { x } FROM { y } WHERE { z }'
                ).fetchall()
            else:
#                print(f'select {x} from {y}')
                result = self.cur.execute(
                    f'SELECT { x } FROM { y }'
                ).fetchall()
            self.cur.close()
            self.con.close()
            return result

        except sqlite3.Error as er:
            print(sqlite_error(er))

    def insert_into_x_values_y(self, x, y):
        self.con = sqlite3.connect(self.path)
        self.cur = self.con.cursor()
        try:
            if "," not in y:
#                print(f'insert into { x } value { y }')
                self.cur.execute(
                    f'INSERT INTO { x } VALUE { y }'
                )
                self.con.commit()
            else:
#                print(f'insert into { x } values { y }')
                self.cur.execute(
                    f'INSERT INTO { x } VALUES ({ y }) '
                )
                self.con.commit()
        except sqlite3.Error as er:
            print(sqlite_error(er))
        self.con.commit()
        self.cur.close()
        self.con.close()

    def insert_into_x_values_y_where_z(self, x, y, z):
        self.con = sqlite3.connect(self.path)
        self.cur = self.con.cursor()
        try:
            if "," not in y:
#                print(f'insert into {x} value {y} where { z }')
                self.cur.execute(
                    f'INSERT INTO {x} VALUE {y} WHERE {z}'
                )
                self.con.commit()
            else:
                self.cur.execute(
                    f'INSERT INTO {x} VALUES ({y}) WHERE {z} '
                )
                self.con.commit()
        except sqlite3.Error as er:
            print(sqlite_error(er))
        self.con.commit()
        self.cur.close()
        self.con.close()

if __name__ == "__main__":
    CelloDB()