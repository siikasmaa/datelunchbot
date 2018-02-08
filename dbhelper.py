import sqlite3
import os

class DBHelper:
    def __init__(self, dbname="menus.db"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self, name):
        stmt = "CREATE TABLE IF NOT EXISTS {n} (ID INT UNIQUE, YEAR INT, WEEK INT, WEEKDAY TEXT, MENU TEXT);".format(n=name)
        self.conn.execute(stmt)
        self.conn.commit()

    def add_item(self, name, args):
        stmt = "INSERT OR IGNORE INTO {n} (WEEKDAY, WEEK, ID, YEAR) VALUES ({a});".format(n=name, a=args)
        self.conn.execute(stmt)
        self.conn.commit()

    def update_item(self, name, menu, id):
        stmt = "UPDATE {n} SET MENU = {m} WHERE ID = {i};".format(n=name, m=menu, i=id)
        self.conn.execute(stmt)
        self.conn.commit()

    def delete_item(self, item_text):
        stmt = "DELETE FROM items WHERE description = (?)"
        args = (item_text)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def select_items(self, name, ide):
        stmt = 'SELECT MENU, WEEKDAY, WEEK FROM {n} WHERE ID = {i}'.format(n=name,i=ide)
        return self.conn.execute(stmt).fetchall()

    def __exit__(self):
        self.conn.close()
