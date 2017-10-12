# -*- coding: utf-8 -*-
import sys
import urllib2
import datetime
import telepot
from telepot.delegate import per_inline_from_id, create_open, pave_event_space
from bs4 import BeautifulSoup

week = datetime.date.today().isocalendar()[1] if (datetime.datetime.today().weekday() < 5) else (datetime.date.today().isocalendar()[1] + 1)

restaurants = [{'type': 'unica', 'title':"Assarin", 'link': 'http://www.unica.fi/index.php?node_id=12533'},
               {'type': 'unica', 'title':"Delica", 'link': 'http://www.unica.fi/fi/ravintolat/delica/'},
               {'type': 'unica', 'title':"Galilei", 'link': 'http://www.unica.fi/fi/ravintolat/galilei/'},
               {'type': 'studentlunch', 'title':'Arken', 'link':'http://www.studentlunch.fi/se/lunchlistan/veckans-lista?id=1&year=2017&week=' + str(week)},
               {'type': 'studentlunch', 'title':'Kåren', 'link': 'http://www.studentlunch.fi/se/lunchlistan/veckans-lista?id=3&year=2017&week=' + str(week)},
               {'type': 'studentlunch', 'title':'Fänriken', 'link':'http://www.studentlunch.fi/se/lunchlistan/veckans-lista?id=4&year=2017&week=' + str(week)},
               {'type': 'studentlunch', 'title':'Gado', 'link': 'http://www.studentlunch.fi/se/lunchlistan/veckans-lista?id=2&year=2017&week=' + str(week)}]

restaurantMenus = [dict() for x in range(len(restaurants))]
dayName = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

def getMenu():
    for x in range(0, len(restaurants)): #Parser for Unica
        req = urllib2.Request(restaurants[x]['link'])
        req.add_header("Content-type", "application/x-www-form-urlencoded")
        page = urllib2.urlopen(req).read()
        soup = BeautifulSoup(page, "lxml")
        if restaurants[x]['type'] == 'unica':
            dayNr = 0
            for day in soup.findAll("div", class_="accord"):
                menuString = ""
                prices = []
                for price in day.findAll("td", class_="price quiet"):
                    prices.append(price.string)
                menuNr = 0
                for menu in day.findAll("td", class_="lunch"):
                    menuString += "\n" + menu.string + "; \n " + ' '.join(prices[menuNr].split()) + "\n"
                    menuNr += 1
                restaurantMenus[x][dayName[dayNr]] = menuString
                dayNr += 1
        else:
            for day in soup.findAll("div", class_="lunch-item-food"):
                prices = []
                for price in day.findAll("td", class_="price-student"):
                    prices.append(price.get_text()[:4 if len(price.get_text()) > 2 else 0:1] + "e")
                dayNr = 0
                menuNr = 0
                for menu in day.findAll("table", class_="week-list"):
                    menuString = ""
                    for food in menu.findAll('a'):
                        menuString += "\n" + food.get_text() + "\n" + prices[menuNr] + "\n"
                        menuNr += 1
                    restaurantMenus[x][dayName[dayNr]] = menuString
                    dayNr += 1
getMenu()


class InlineHandler(telepot.helper.InlineUserHandler, telepot.helper.AnswererMixin):
    def __init__(self, *args, **kwargs):
        super(InlineHandler, self).__init__(*args, **kwargs)

    def on_inline_query(self, msg):
        def compute_answer():
            query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
            currWeekDay = datetime.datetime.today().weekday()
            maxDateWOWknd = currWeekDay if (currWeekDay < 5) else 0 #If restaurant doesn't have menus for weekends, the query responds with monday (next weeks, if available)
            maxDateWSat = currWeekDay if (currWeekDay < 6) else 0
            articles = [{'type': 'article', 'id': 'assari', 'title': restaurants[0]["title"], 'message_text': "Assarin ullakko, " + dayName[maxDateWSat] + " :" + restaurantMenus[0][dayName[maxDateWSat]]},
                        {'type': 'article', 'id': 'delica', 'title': restaurants[1]["title"], 'message_text': "Delica, " + dayName[maxDateWOWknd] + " :" + restaurantMenus[1][dayName[maxDateWOWknd]]},
                        {'type': 'article', 'id': 'galilei', 'title': restaurants[2]["title"], 'message_text': "Galilei, " + dayName[maxDateWOWknd] + " :" + restaurantMenus[2][dayName[maxDateWOWknd]]},
                        {'type': 'article', 'id': 'arken', 'title': restaurants[3]["title"], 'message_text': "Arken, " + dayName[maxDateWOWknd] + " :" + restaurantMenus[3][dayName[maxDateWOWknd]]},
                        {'type': 'article', 'id': 'karen', 'title': restaurants[4]["title"], 'message_text': "Karen, " + dayName[maxDateWOWknd] + " :" + restaurantMenus[4][dayName[maxDateWOWknd]]},
                        {'type': 'article', 'id': 'fanriken', 'title': restaurants[5]["title"], 'message_text': "Fanriken, " + dayName[maxDateWOWknd] + " :" + restaurantMenus[5][dayName[maxDateWOWknd]]},
                        {'type': 'article', 'id': 'gado', 'title': restaurants[6]["title"], 'message_text': "Gado, " + dayName[maxDateWOWknd] + " :" + restaurantMenus[6][dayName[maxDateWOWknd]]},
                        ]
            return articles
        self.answerer.answer(msg, compute_answer)

    def on_chosen_inline_result(self, msg):
        result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
        print(self.id, ':', 'Chosen Inline Result:', result_id, from_id, query_string)


TOKEN = sys.argv[1]
bot = telepot.DelegatorBot(TOKEN, [pave_event_space()(per_inline_from_id(), create_open, InlineHandler, timeout=10),])
print("Listening...")
