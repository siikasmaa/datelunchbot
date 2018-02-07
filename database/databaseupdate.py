# -*- coding: utf-8 -*-
import sys
import urllib2
import datetime
import calendar
import json
import re
import io
import sqlite3 as sql
from dbhelper import DBHelper
from bs4 import BeautifulSoup

db = DBHelper()

def updateDb():
    for x in range(len(restaurants)):
        try:
            db.setup(restaurants[x]['title'].encode('utf-8'))
            print "Table for {r} created successfully".format(r=restaurants[x]['title'].encode('utf-8'))
        except sql.OperationalError:
            print "Table for {r} exists already!".format(r=restaurants[x]['title'].encode('utf-8'))
        req = urllib2.Request(restaurants[x]['link'])
        req.add_header('Content-type', 'application/x-www-form-urlencoded')
        urllib2.urlopen(req).read()
        page = urllib2.urlopen(req).read()
        soup = BeautifulSoup(page, 'lxml')
        if restaurants[x]['type'] == 'unica': #Parser for Unica
            dayNr = 0
            for day in soup.findAll('div', class_='accord'):
                print "Inserting new rows"
                try:
                    db.add_item(restaurants[x]['title'].encode('utf-8'), "{wd}, {w}, {id}, {y}".format(wd="'"+calendar.day_name[dayNr]+"'",w=week,y=year,id=int(str(dayNr)+str(week)+str(year))))
                    prices = []
                    foods = []
                    menuNr = 0
                    for price in day.findAll('td', class_='price quiet'):
                        prices.append(unicode(re.sub('[;\n 	]', '', price.string.strip().replace("'",""))))
                    for menu in day.findAll('td', class_='lunch'):
                        foods.append(unicode(re.sub('[;"/-]','', menu.string.replace("'",""))))
                        menuNr += 1
                    foods = dict(zip(foods,prices))
                    db.update_item(restaurants[x]['title'].encode('utf-8'),'"'+str(foods).encode('utf-8', 'strict')+'"', int(str(dayNr)+str(week)+str(year)))
                except sql.OperationalError as e:
                    print e
                finally:
                    dayNr += 1
        else: #Parser for Kårkaféerna
            for day in soup.findAll('div', class_='lunch-item-food'):
                prices = []
                for price in day.findAll('td', class_='price-student'):
                    prices.append(unicode(price.get_text()[:4 if len(price.get_text()) > 2 else 0:1] + 'e'))
                dayNr = 0
                menuNr = 0
                for menu in day.findAll('table', class_='week-list'):
                    try:
                        print "Inserting new rows"
                        db.add_item(restaurants[x]['title'].encode('utf-8'), "{wd}, {w}, {id}, {y}".format(wd="'"+calendar.day_name[dayNr]+"'",w=week,y=year,id=int(str(dayNr)+str(week)+str(year))))
                        foods = []
                        for food in menu.findAll('a'):
                            foods.append(unicode(re.sub('''[;"'/-]''','',food.get_text())))
                        foods = dict(zip(foods,prices))
                        db.update_item(restaurants[x]['title'].encode('utf-8'),'"'+str(foods).encode('utf-8', 'strict')+'"', int(str(dayNr)+str(week)+str(year)))
                        dayNr += 1
                    except sql.OperationalError as e:
                        print e

if __name__ == "__main__":
    week = datetime.date.today().isocalendar()[1] if (datetime.datetime.today().weekday() < 5) else (datetime.date.today().isocalendar()[1] + 1)
    year = datetime.date.today().isocalendar()[0]
    with io.open('../restaurants.json', encoding='utf-8') as json_data:
        restaurants = json.load(json_data)
    updateDb()
