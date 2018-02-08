# -*- coding: utf-8 -*-
import sys, os
import logging
import argparse
import datetime
import telepot
import json
import ast
import io
from telepot.loop import MessageLoop
from dbhelper import DBHelper
from telepot.delegate import per_inline_from_id, create_open, pave_event_space
from telepot.helper import InlineUserHandler, AnswererMixin

restaurants = {}

class InlineHandler(InlineUserHandler, AnswererMixin):
    def __init__(self, *args, **kwargs):
        super(InlineHandler, self).__init__(*args, **kwargs)

    def on_inline_query(self, msg):
        db = DBHelper()
        week = datetime.date.today().isocalendar()[1] if (datetime.datetime.today().weekday() < 5) else (datetime.date.today().isocalendar()[1] + 1)
        year = datetime.date.today().isocalendar()[0]

        def compute_answer():
            query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
            logging.info(query_id, from_id, query_string)
            max_date_wo_wknd = datetime.datetime.today().weekday() if (datetime.datetime.today().weekday() < 6) else 0
            ide = int(str(max_date_wo_wknd)+str(week)+str(year))
            articles = []
            try:
                for i in range(len(restaurants)):
                    lis = ""
                    i=0
                    cursor = db.select_items(restaurants[i]['title'].encode('utf-8'), ide)
                    for key, value in ast.literal_eval(cursor[0][0]).iteritems():
                        lis += key + "\n " + value + "\n\n"
                    articles.append({'id': restaurants[i]['id'], 'type': 'article', 'title': restaurants[i]['title'].encode('utf-8'), 'thumb_url': restaurants[i]['thumb'], 'url': restaurants[i]['link'], 'message_text': restaurants[i]['title'] + ', ' + cursor[0][1] + ', week: ' + str(cursor[0][2]) + ' \n' + lis})
            except Exception as e:
                logging.error(e)
            return articles
        self.answerer.answer(msg, compute_answer)

    def on_chosen_inline_result(self, msg):
        result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
        logging.info(self.id, ':', 'Chosen Inline Result:', result_id, from_id, query_string)

def main(loggingfile,TOKEN):
    with io.open(os.path.abspath("./restaurants.json"), encoding='utf-8') as json_data:
        restaurants = json.load(json_data)
    logging.basicConfig(filename=loggingfile+'.log',format='%(asctime)-15s %(message)s')
    bot = telepot.DelegatorBot(TOKEN, [pave_event_space()(per_inline_from_id(), create_open, InlineHandler, timeout=10),])
    bot.message_loop(run_forever='Listening ...')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', type=str, help="Telegram bot token obtained from Botfather.")
    parser.add_argument('-f', '--file', type=str, help="Filename for logfile.")
    args = parser.parse_args()
    main(args.file,args.token)
