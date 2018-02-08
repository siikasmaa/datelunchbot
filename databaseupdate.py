# -*- coding: utf-8 -*-
import sys, os
import datetime
import calendar
import json
import re
import io
from bs4 import BeautifulSoup
from restaurant import Restaurant

def update_db():
    for item in restaurants:
        res = Restaurant(item)
        res.setup_db()
        if res.type == 'unica':
            unica_parser(res.query(), res)
        if res.type == 'studentlunch':
            studentlunch_parser(res.query(), res)

def unica_parser(parsed_page, res):
    day_nr = 0
    for day in parsed_page.findAll('div', class_='accord'):
        print "Inserting new rows"
        res.add_db_item("{wd}, {w}, {id}, {y}".format(wd="'"+calendar.day_name[day_nr]+"'",w=week,y=year,id=int(str(day_nr)+str(week)+str(year))))
        prices = []
        foods = []
        menu_nr = 0
        for price in day.findAll('td', class_='price quiet'):
            prices.append(unicode(re.sub('[;\n\t]', '', price.string.strip().replace("'",""))))
        for menu in day.findAll('td', class_='lunch'):
            foods.append(unicode(re.sub('''[;"'/-]''','', menu.string)))
            menu_nr += 1
        foods = dict(zip(foods,prices))
        res.update_db_item(str(foods).encode('utf-8', 'strict'), int(str(day_nr)+str(week)+str(year)))
        day_nr += 1

def studentlunch_parser(parsed_page, res):
    for day in parsed_page.findAll('div', class_='lunch-item-food'):
        prices = []
        day_nr = 0
        menu_nr = 0
        for price in day.findAll('td', class_='price-student'):
            prices.append(unicode(price.get_text()[:4 if len(price.get_text()) > 2 else 0:1] + 'e'))
        for menu in day.findAll('table', class_='week-list'):
            print "Inserting new rows"
            res.add_db_item("{wd}, {w}, {id}, {y}".format(wd="'"+calendar.day_name[day_nr]+"'",w=week,y=year,id=int(str(day_nr)+str(week)+str(year))))
            foods = []
            for food in menu.findAll('a'):
                foods.append(unicode(re.sub('''[;"'/-]''','',food.get_text())))
            foods = dict(zip(foods,prices))
            res.update_db_item(str(foods).encode('utf-8', 'strict'), int(str(day_nr)+str(week)+str(year)))
            day_nr += 1

if __name__ == "__main__":
    week = datetime.date.today().isocalendar()[1] if (datetime.datetime.today().weekday() < 5) else (datetime.date.today().isocalendar()[1] + 1)
    year = datetime.date.today().isocalendar()[0]
    with io.open(os.path.abspath("./restaurants.json"), encoding='utf-8') as json_data:
        restaurants = json.load(json_data)
    update_db()
