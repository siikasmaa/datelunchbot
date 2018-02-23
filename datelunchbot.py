# -*- coding: utf-8 -*-
import sys, os
import logging
import argparse
import datetime, time
import telepot
import json
import ast
import io
import geopy.distance
from operator import itemgetter
from dbhelper import DBHelper
from telepot.namedtuple import KeyboardButton, ReplyKeyboardRemove
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import per_inline_from_id, create_open, pave_event_space, per_chat_id, include_callback_query_chat_id
from telepot.helper import InlineUserHandler, AnswererMixin, ChatHandler
from datadog import initialize, ThreadStats

with io.open(os.path.abspath("./restaurants.json"), encoding='utf-8') as json_data:
    restaurants = json.load(json_data)
message_with_inline_keyboard = None
stats = ThreadStats()

class MessageHandler(ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MessageHandler, self).__init__(*args, **kwargs)

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type != 'text':
            return

        command = msg['text'].lower()

        if command == '/language':
            stats.increment('language.calls')
            markup = InlineKeyboardMarkup(inline_keyboard=[
             [InlineKeyboardButton(text='Swedish', callback_data='swedish')],
             [InlineKeyboardButton(text='Finnish', callback_data='finnish')],
             [InlineKeyboardButton(text='English', callback_data='english')]
                 ])

            global message_with_inline_keyboard
            message_with_inline_keyboard = self.sender.sendMessage('Select language for menus', reply_markup=markup)

        elif command == 'h':
            markup = ReplyKeyboardRemove()
            self.sender.sendMessage('Hide custom keyboard', reply_markup=markup)

    def _close(self, from_id, data):
        stats.increment('language.'+data+'.selected')
        with DBHelper() as db:
            db.setup("Preferences", "ID INT UNIQUE, LANGUAGE TEXT")
            db.add_item("Preferences", "ID, LANGUAGE", "{f}, '{d}'".format(f=from_id, d=data))
            db.update_item("Preferences", "LANGUAGE", "'{d}'".format(d=data), from_id)

    def on_callback_query(self, msg):
        query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
        if data == 'swedish':
            self.sender.sendMessage('Swedish selected')
            data = 'se'
        elif data == 'finnish':
            self.sender.sendMessage('Finnish selected')
        elif data == 'english':
            self.sender.sendMessage('English selected')
        self._close(from_id, data[:2])


class InlineHandler(InlineUserHandler, AnswererMixin):
    def __init__(self, *args, **kwargs):
        super(InlineHandler, self).__init__(*args, **kwargs)

    def on_inline_query(self, msg):
        week = datetime.date.today().isocalendar()[1]
        year = datetime.date.today().isocalendar()[0]
        global restaurants
        if 'location' in msg:
            stats.increment('location.query')
            coords_1 = (msg['location']['latitude'], msg['location']['longitude'])
            for res in restaurants:
                coords_2 = (res['lat'], res['lng'])
                res['distance'] = geopy.distance.vincenty(coords_1, coords_2).m
            restaurants = sorted(restaurants, key=itemgetter('distance'))

        def compute_answer():
            start = time.time()
            query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
            stats.increment('user.'+str(from_id)+'.call')
            max_date_wo_wknd = datetime.datetime.today().weekday() if (datetime.datetime.today().weekday() < 6) else 0
            ide = int(str(max_date_wo_wknd)+str(week)+str(year))
            articles = []
            lang = 'en'
            with DBHelper() as db:
                if db.select_lang(msg['from']['id']):
                    lang = db.select_lang(msg['from']['id'])[0][0]
                for i in range(len(restaurants)):
                    lis = ""
                    cursor = db.select_items(lang.upper(), restaurants[i]['id'].encode('utf-8'), ide)
                    if not cursor[0][0]:
                        cursor = db.select_items("EN", restaurants[i]['id'].encode('utf-8'), ide)
                    for key, value in ast.literal_eval(cursor[0][0]).iteritems():
                        lis += key + "\n " + value + "\n\n"
                    if 'query' in msg:
                        if msg['query'].lower() in restaurants[i]['title'].lower():
                            articles.append({'id': restaurants[i]['id'], 'type': 'article', 'title': restaurants[i]['title'].encode('utf-8'), 'thumb_url': restaurants[i]['thumb'], 'message_text': restaurants[i]['title'] + ', ' + cursor[0][1] + ', week: ' + str(cursor[0][2]) + ' \n' + lis})
                    else:
                        articles.append({'id': restaurants[i]['id'], 'type': 'article', 'title': restaurants[i]['title'].encode('utf-8'), 'thumb_url': restaurants[i]['thumb'], 'message_text': restaurants[i]['title'] + ', ' + cursor[0][1] + ', week: ' + str(cursor[0][2]) + ' \n' + lis})
            stats.histogram('user.query.time', time.time() - start)
            return articles

        self.answerer.answer(msg, compute_answer)

    def on_chosen_inline_result(self, msg):
        result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
        stats.increment('selection.'+result_id)

def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def main(loggingfile,TOKEN):
    logging.basicConfig(filename=loggingfile+'.log',format='%(asctime)-15s %(message)s')
    bot = telepot.DelegatorBot(TOKEN, [pave_event_space()(per_inline_from_id(), create_open, InlineHandler, timeout=1), include_callback_query_chat_id(pave_event_space())(
        per_chat_id(), create_open, MessageHandler, timeout=1)])
    bot.message_loop(run_forever='Listening ...')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', type=str, help="Telegram bot token obtained from Botfather.")
    parser.add_argument('-f', '--file', type=str, help="Filename for logfile.")
    parser.add_argument('-a', '--api', type=str, help="Datadog api_key.")
    parser.add_argument('-p', '--app', type=str, help="Datadog app_key.")
    args = parser.parse_args()
    if (args.api != None and args.app != None):
        options = {
            'api_key':args.api,
            'app_key':args.app
            }
        initialize(**options)
        stats.start()
    else:
        stats.start(disabled=True)
    main(args.file,args.token)
