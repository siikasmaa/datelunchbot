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

    def setup(self, name):
        try:
            stmt = "CREATE TABLE IF NOT EXISTS {n} (ID INT UNIQUE, YEAR INT, WEEK INT, WEEKDAY TEXT, MENU TEXT);".format(n=name)
            self.conn.execute(stmt)
            self.conn.commit()
        except sql.OperationalError as e:
            self.conn.rollback()
            print e

    def add_item(self, name, args):
        try:
            stmt = "INSERT OR IGNORE INTO {n} (WEEKDAY, WEEK, ID, YEAR) VALUES ({a});".format(n=name, a=args)
            self.conn.execute(stmt)
            self.conn.commit()
        except sql.OperationalError as e:
            self.conn.rollback()
            print e

    def update_item(self, name, menu, id):
        try:
            stmt = "UPDATE {n} SET MENU = {m} WHERE ID = {i};".format(n=name, m=menu, i=id)
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

    def select_items(self, name, ide):
        try:
            stmt = 'SELECT MENU, WEEKDAY, WEEK FROM {n} WHERE ID = {i}'.format(n=name,i=ide)
            return self.conn.execute(stmt).fetchall()
        except sql.OperationalError as e:
            print e

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.conn.close()
            print "Connection to {n} closed succesfully".format(n=self.dbname)
        except sql.OperationalError as e:
            print e
