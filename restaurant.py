import urllib2
from bs4 import BeautifulSoup

class Restaurant:
    def __init__(self, item):
        self.title = item['title'].encode('utf-8')
        self.link = item['link']
        self.type = item['type']
        self.id = item['id']

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
