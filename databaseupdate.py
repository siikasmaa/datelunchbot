# -*- coding: utf-8 -*-
import sys, os
import argparse
import datetime
import calendar
import json
import re
import io
from bs4 import BeautifulSoup
from dbhelper import DBHelper
from restaurant import Restaurant

db_file = "menus.db"

def update_db(db_file):
    with DBHelper(db_file) as db:
        for item in restaurants:
            res = Restaurant(item)
            db.setup(res.id, "ID INT UNIQUE, YEAR INT, WEEK INT, WEEKDAY TEXT, MENUFI TEXT, MENUSE TEXT, MENUEN TEXT")
            for link in res.links:
                if res.type == 'unica':
                    unica_parser(res.query(link.items()[0][1]), link.items()[0][0], res, db)
                if res.type == 'studentlunch':
                    studentlunch_parser(res.query(link.items()[0][1]), link.items()[0][0], res, db)
            print "Database for {r} setup succesfully".format(r=res.title)

def unica_parser(parsed_page, lang, res, db):
    day_nr = 0
    for day in parsed_page.findAll('div', class_='accord'):
        db.add_item(res.id, "WEEKDAY, WEEK, ID, YEAR", "{wd}, {w}, {id}, {y}".format(wd="'"+calendar.day_name[day_nr]+"'",w=week,y=year,id=int(str(day_nr)+str(week)+str(year))))
        prices = []
        foods = []
        for price in day.findAll('td', class_='price quiet'):
            prices.append(unicode(re.sub('[;\n\t]', '', price.string.strip().replace("'",""))))
        for menu in day.findAll('td', class_='lunch'):
            foods.append(unicode(re.sub('''["'/]''','', menu.string.replace(';',':'))))
        foods = dict(zip(foods,prices))
        db.update_item(res.id, "MENU"+lang.upper(), '"'+str(foods).encode('utf-8', 'strict')+'"', int(str(day_nr)+str(week)+str(year)))
        day_nr += 1

def studentlunch_parser(parsed_page, lang, res, db):
    day_nr = 0
    price_dict = {"se":"Pris: ", "fi":"Hinta: ", "en":"Price: "}
    for day in parsed_page.findAll('table', class_='week-list'):
        db.add_item(res.id, "WEEKDAY, WEEK, ID, YEAR", "{wd}, {w}, {id}, {y}".format(wd="'"+calendar.day_name[day_nr]+"'",w=week,y=year,id=int(str(day_nr)+str(week)+str(year))))
        foods = []
        prices = []
        for row in day.findAll('tr'):
            price_string = price_dict[lang]
            for price in row.findAll('td', class_=re.compile('price-*')):
                price_string += price.get_text() + " / "
            prices.append(unicode(price_string[:-2]))
            for food in row.findAll('td', class_='food'):
                foods.append(unicode(re.sub('''["'/]''','',food.get_text().replace(';',':'))))
        foods = dict(zip(foods,prices))
        db.update_item(res.id, "MENU"+lang.upper(), '"'+str(foods).encode('utf-8', 'strict')+'"', int(str(day_nr)+str(week)+str(year)))
        day_nr += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--db', type=str, help="Database file location.")
    args = parser.parse_args()
    week = datetime.date.today().isocalendar()[1]
    year = datetime.date.today().isocalendar()[0]
    if (args.db != None):
        db_file = args.db
    with io.open(os.path.abspath("./restaurants.json"), encoding='utf-8') as json_data:
        restaurants = json.load(json_data)
    update_db(db_file)
