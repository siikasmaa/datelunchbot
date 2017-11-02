# -*- coding: utf-8 -*-
import sys
import urllib2
import time
import datetime
import telepot
from telepot.loop import MessageLoop
from telepot.delegate import per_inline_from_id, create_open, pave_event_space
from telepot.helper import InlineUserHandler, AnswererMixin
from bs4 import BeautifulSoup

week = datetime.date.today().isocalendar()[1] if (datetime.datetime.today().weekday() < 5) else (datetime.date.today().isocalendar()[1] + 1)
year = datetime.date.today().isocalendar()[0]

restaurants = [{'type': 'unica', 'title':'Assarin', 'link': 'http://www.unica.fi/fi/ravintolat/assarin-ullakko/', 'thumb': 'http://www.unica.fi/images/uploads/assari.jpg', 'lat': '60.4542999267578', 'lng': '22.2875003814697'},
               {'type': 'unica', 'title':'Delica', 'link': 'http://www.unica.fi/fi/ravintolat/delica/', 'thumb': 'http://www.unica.fi/images/uploads/delica.jpg', 'lat':'60.4488983154297', 'lng':'22.2926006317139'},
               {'type': 'unica', 'title':'Galilei', 'link': 'http://www.unica.fi/fi/ravintolat/galilei/', 'thumb': 'http://www.unica.fi/images/uploads/Galilei_ulko.jpg', 'lat': '60.45559499999999', 'lng': '22.286412700000028'},
               {'type': 'unica', 'title': 'Dental', 'link': 'http://www.unica.fi/fi/ravintolat/dental/', 'thumb': 'http://www.unica.fi/images/uploads/dental.jpg', 'lat':'60.4499531979394', 'lng':'22.2924307185242'},
               {'type': 'studentlunch', 'title':'Arken', 'link':'http://www.studentlunch.fi/se/lunchlistan/veckans-lista?id=1&year=' + str(year) +'&week=' + str(week), 'thumb': 'http://www.studentlunch.fi/assets/images/logos/restaurant_1.jpg', 'lat': '60.4566993713379', 'lng': '22.2786998748779'},
               {'type': 'studentlunch', 'title':u'Kåren', 'link': 'http://www.studentlunch.fi/se/lunchlistan/veckans-lista?id=3&year=' + str(year) +'&week=' + str(week), 'thumb': 'http://www.studentlunch.fi/assets/images/logos/restaurant_3.jpg', 'lat':'60.4496002197266', 'lng':'22.2754001617432'},
               {'type': 'studentlunch', 'title':u'Fänriken', 'link':'http://www.studentlunch.fi/se/lunchlistan/veckans-lista?id=4&year=' + str(year) +'&week=' + str(week), 'thumb': 'http://www.studentlunch.fi/assets/images/logos/restaurant_4.jpg', 'lat': '60.456600189209', 'lng': '22.2826995849609'},
               {'type': 'studentlunch', 'title':'Gado', 'link': 'http://www.studentlunch.fi/se/lunchlistan/veckans-lista?id=2&year=' + str(year) +'&week=' + str(week), 'thumb': 'http://www.studentlunch.fi/assets/images/logos/restaurant_2.jpg', 'lat': '60.4541015625', 'lng': '22.2793006896973'}]

restaurantMenus = [dict() for x in range(len(restaurants))]
dayName = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

def getMenu():
    week = datetime.date.today().isocalendar()[1] if (datetime.datetime.today().weekday() < 5) else (datetime.date.today().isocalendar()[1] + 1)
    year = datetime.date.today().isocalendar()[0]
    print 'Fetching menu'
    for x in range(0, len(restaurants)):
        req = urllib2.Request(restaurants[x]['link'])
        req.add_header('Content-type', 'application/x-www-form-urlencoded')
        page = urllib2.urlopen(req).read()
        soup = BeautifulSoup(page, 'lxml')
        if restaurants[x]['type'] == 'unica': #Parser for Unica
            dayNr = 0
            for day in soup.findAll('div', class_='accord'):
                menuString = ''
                prices = []
                for price in day.findAll('td', class_='price quiet'):
                    prices.append(price.string)
                menuNr = 0
                for menu in day.findAll('td', class_='lunch'):
                    menuString += '\n' + menu.string + '; \n ' + ' '.join(prices[menuNr].split()) + '\n'
                    menuNr += 1
                restaurantMenus[x][dayName[dayNr]] = menuString
                dayNr += 1
        else: #Parser for Kårkaféerna
            for day in soup.findAll('div', class_='lunch-item-food'):
                prices = []
                for price in day.findAll('td', class_='price-student'):
                    prices.append(price.get_text()[:4 if len(price.get_text()) > 2 else 0:1] + 'e')
                dayNr = 0
                menuNr = 0
                for menu in day.findAll('table', class_='week-list'):
                    menuString = ''
                    for food in menu.findAll('a'):
                        menuString += '\n' + food.get_text() + '\n' + prices[menuNr] + '\n'
                        menuNr += 1
                    restaurantMenus[x][dayName[dayNr]] = menuString
                    dayNr += 1

class InlineHandler(InlineUserHandler, AnswererMixin):
    def __init__(self, *args, **kwargs):
        super(InlineHandler, self).__init__(*args, **kwargs)

    def on_inline_query(self, msg):
        def compute_answer():
            query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
            print(query_id, from_id, query_string)
            currWeekDay = datetime.datetime.today().weekday()
            maxDateWOWknd = currWeekDay if (currWeekDay < 5) else 0 #If restaurant doesn't have menus for weekends, the query responds with monday (next week, if available)
            maxDateWSat = currWeekDay if (currWeekDay < 6) else 0
            articles = [{'type': 'article', 'id': 'assari', 'title': restaurants[0]['title'], 'thumb_url': restaurants[0]['thumb'], 'url': restaurants[0]['link'], 'message_text': restaurants[0]['title'] + ', ' + dayName[maxDateWSat] + ' :' + restaurantMenus[0][dayName[maxDateWSat]], 'latitude': restaurants[0]['lat']},
                        {'type': 'article', 'id': 'delica', 'title': restaurants[1]['title'], 'thumb_url': restaurants[1]['thumb'], 'url': restaurants[1]['link'], 'message_text': restaurants[1]['title'] + ', ' + dayName[maxDateWOWknd] + ' :' + restaurantMenus[1][dayName[maxDateWOWknd]]},
                        {'type': 'article', 'id': 'galilei', 'title': restaurants[2]['title'], 'thumb_url': restaurants[2]['thumb'], 'url': restaurants[2]['link'], 'message_text': restaurants[2]['title'] + ', ' + dayName[maxDateWOWknd] + ' :' + restaurantMenus[2][dayName[maxDateWOWknd]]},
                        {'type': 'article', 'id': 'dental', 'title': restaurants[3]['title'], 'thumb_url': restaurants[3]['thumb'], 'url': restaurants[3]['link'], 'message_text': restaurants[3]['title'] + ', ' + dayName[maxDateWOWknd] + ' :' + restaurantMenus[3][dayName[maxDateWOWknd]]},
                        {'type': 'article', 'id': 'arken', 'title': restaurants[4]['title'], 'thumb_url': restaurants[4]['thumb'], 'url': restaurants[4]['link'], 'message_text': restaurants[4]['title'] + ', ' + dayName[maxDateWOWknd] + ' :' + restaurantMenus[4][dayName[maxDateWOWknd]]},
                        {'type': 'article', 'id': 'karen', 'title': restaurants[5]['title'], 'thumb_url': restaurants[5]['thumb'], 'url': restaurants[5]['link'], 'message_text': restaurants[5]['title'] + ', ' + dayName[maxDateWOWknd] + ' :' + restaurantMenus[5][dayName[maxDateWOWknd]]},
                        {'type': 'article', 'id': 'fanriken', 'title': restaurants[6]['title'], 'thumb_url': restaurants[6]['thumb'], 'url': restaurants[6]['link'], 'message_text': restaurants[6]['title'] + ', ' + dayName[maxDateWOWknd] + ' :' + restaurantMenus[6][dayName[maxDateWOWknd]]},
                        {'type': 'article', 'id': 'gado', 'title': restaurants[7]['title'], 'thumb_url': restaurants[7]['thumb'], 'url': restaurants[7]['link'], 'message_text': restaurants[7]['title'] + ', ' + dayName[maxDateWOWknd] + ' :' + restaurantMenus[7][dayName[maxDateWOWknd]]},
                        ]
            return articles
        self.answerer.answer(msg, compute_answer)

    def on_chosen_inline_result(self, msg):
        result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
        print(self.id, ':', 'Chosen Inline Result:', result_id, from_id, query_string)

def main():
    getMenu()
    TOKEN = sys.argv[1]
    bot = telepot.DelegatorBot(TOKEN, [pave_event_space()(per_inline_from_id(), create_open, InlineHandler, timeout=60),])
    MessageLoop(bot).run_as_thread()
    print('Listening ...')
    while 1:
        time.sleep(80000)
        getMenu()

if __name__ == '__main__':
    main()
