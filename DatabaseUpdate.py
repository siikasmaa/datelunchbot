# -*- coding: utf-8 -*-
import sys
import urllib2
import datetime
import json
import sqlite3 as sql
from bs4 import BeautifulSoup

def updateDb():
    c = sql.connect('menus.db')
    conn = c.cursor()
    print "Opened database succesfully!"
    print 'Fetching menus!'
    for x in range(0, len(restaurants)):
        try:
            conn.execute("CREATE TABLE IF NOT EXISTS {r} (ID INT UNIQUE, YEAR INT, WEEK INT, WEEKDAY TEXT, MENU TEXT, PRICES TEXT);".format(r=restaurants[x]['title'].encode('utf8')))
            print "Table for {r} created successfully".format(r=restaurants[x]['title'].encode('utf8'))
        except sql.OperationalError:
            print "Table for {r} exists already!".format(r=restaurants[x]['title'])
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
                    conn.execute("INSERT OR IGNORE INTO {r} (WEEKDAY, WEEK, ID, YEAR) VALUES ({wd}, {w}, {id}, {y});".format(r=restaurants[x]['title'],wd="'"+dayName[dayNr]+"'",w=week,y=year,id=int(str(dayNr)+str(week)+str(year))));
                    prices = []
                    foods = []
                    menuNr = 0
                    for price in day.findAll('td', class_='price quiet'):
                        prices.append(unicode(price.string.strip().replace(";","").replace("\n", "").replace("	","")))
                    for menu in day.findAll('td', class_='lunch'):
                        foods.append(unicode(menu.string.strip().replace(";","")))
                        menuNr += 1
                    foods = dict(zip(foods,prices))
                    conn.execute("UPDATE {r} SET MENU = {m} WHERE ID = {id};".format(r=restaurants[x]['title'], m='"'+str(foods).encode('utf-8', 'strict')+'"', wd="'"+dayName[dayNr]+"'",w=week,id=int(str(dayNr)+str(week)+str(year))))
                    dayNr += 1
                except sql.OperationalError as e:
                    print e
        else: #Parser for Kårkaféerna
            for day in soup.findAll('div', class_='lunch-item-food'):
                prices = []
                for price in day.findAll('td', class_='price-student'):
                    prices.append((price.get_text()[:4 if len(price.get_text()) > 2 else 0:1] + 'e'))
                dayNr = 0
                menuNr = 0
                for menu in day.findAll('table', class_='week-list'):
                    try:
                        print "Inserting new rows"
                        conn.execute("INSERT OR IGNORE INTO {r} (WEEKDAY, WEEK, ID, YEAR) VALUES ({wd}, {w}, {id}, {y});".format(r=restaurants[x]['title'].encode('utf8'),wd="'"+dayName[dayNr]+"'",w=week,y=year,id=int(str(dayNr)+str(week)+str(year))));
                        foods = []
                        for food in menu.findAll('a'):
                            foods.append(food.get_text().encode('utf8').replace(";",""))
                        conn.execute("UPDATE {r} SET MENU = {m},PRICES = {p} WHERE ID = {id};".format(r=restaurants[x]['title'].encode('utf8'), m="'"+"|".join(foods)+"'", wd="'"+dayName[dayNr]+"'",p="'"+",".join(prices)+"'",w=week,id=int(str(dayNr)+str(week)+str(year))))
                        dayNr += 1
                    except sql.OperationalError as e:
                        print e
    c.commit()
    c.close()

if __name__ == "__main__":
    week = datetime.date.today().isocalendar()[1] if (datetime.datetime.today().weekday() < 5) else (datetime.date.today().isocalendar()[1] + 1)
    year = datetime.date.today().isocalendar()[0]
    restaurants = {}
    with open('restaurants.json') as json_data:
        restaurants = json.load(json_data)
    dayName = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    updateDb()
