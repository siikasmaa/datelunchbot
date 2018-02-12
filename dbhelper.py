import sqlite3 as sql
import os

class DBHelper:
    def __enter__(self, dbname="menus.db"):
        try:
            self.dbname = dbname
            self.conn = sql.connect(dbname)
            print "Connection to {n} established".format(n=dbname)
            return self
        except sql.OperationalError as e:
            self.conn.rollback()
            print e

    def setup(self, name, cols):
        try:
            stmt = "CREATE TABLE IF NOT EXISTS {n} ({c});".format(n=name, c=cols)
            self.conn.execute(stmt)
            self.conn.commit()
        except sql.OperationalError as e:
            self.conn.rollback()
            print e

    def add_item(self, name, cols, args):
        try:
            stmt = "INSERT OR REPLACE INTO {n} ({c}) VALUES ({a});".format(n=name, c=cols, a=args)
            self.conn.execute(stmt)
            self.conn.commit()
        except sql.OperationalError as e:
            self.conn.rollback()
            print e

    def update_item(self, name, lang, menu, id):
        try:
            stmt = "UPDATE {n} SET {l} = {m} WHERE ID = {i};".format(n=name, l="MENU"+lang, m=menu, i=id)
            self.conn.execute(stmt)
            self.conn.commit()
        except sql.OperationalError as e:
            self.conn.rollback()
            print e

    def delete_item(self, item_text):
        try:
            stmt = "DELETE FROM items WHERE description = (?)"
            args = (item_text)
            self.conn.execute(stmt, args)
            self.conn.commit()
        except sql.OperationalError as e:
            self.conn.rollback()
            print e

    def select_items(self, lang, name, ide):
        try:
            stmt = 'SELECT MENU{l}, WEEKDAY, WEEK FROM {n} WHERE ID = {i}'.format(n=name, l=lang, i=ide)
            return self.conn.execute(stmt).fetchall()
        except sql.OperationalError as e:
            print e

    def select_lang(self, ide):
        try:
            stmt = 'SELECT LANGUAGE FROM Preferences WHERE ID = {i}'.format(i=ide)
            return self.conn.execute(stmt).fetchall()
        except sql.OperationalError as e:
            print e

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.conn.close()
            print "Connection to {n} closed succesfully".format(n=self.dbname)
        except sql.OperationalError as e:
            print e
