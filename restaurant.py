import urllib2
from dbhelper import DBHelper
from bs4 import BeautifulSoup

db = DBHelper()

class Restaurant:
    def __init__(self, item):
        self.title = item['title'].encode('utf-8')
        self.link = item['link']
        self.type = item['type']
        self.id = item['id']

    def setup_db(self):
        try:
            db.setup(self.title)
            print "Table for {r} created successfully".format(r=self.title)
        except sql.OperationalError as e:
            print "Error creating table for {r}".format(r=self.title)
            print e

    def query(self):
        parsed_page = ''
        try:
            req = urllib2.Request(self.link)
            req.add_header('Content-type', 'application/x-www-form-urlencoded')
            urllib2.urlopen(req).read()
            page = urllib2.urlopen(req).read()
            parsed_page = BeautifulSoup(page, 'lxml')
        except Exception as e:
            print "Error connecting to {l}".format(l=self.link)
            print e
        return parsed_page

    def add_db_item(self, args):
        db.add_item(self.title, args)

    def update_db_item(self, menu, row_id):
        db.update_item(self.title,'"'+menu+'"', row_id)
