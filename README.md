# LunchBot
Telegram bot in Python for fetching studentlunch menus in Turku.

You can try it live at https://telegram.me/datelunchbot

Currently there are 9 restaurants available:

Restaurant | Studentlunch/Unica |
---------- | ---------- |
Arken | Studentlunch
Assarin ullakko | Unica
Delica | Unica
Deli Pharma | Unica
Dental | Unica
Fänriken | Studentlunch
Gado | Studentlunch
Galilei | Unica
Kåren | Studentlunch

## Installation
-------------

DateLunchBot uses a database to store the menus. The SQLite database for the menus can be created with databaseupdate.py

In order to run DateLunchBot, you need a Telegram Bot Token from [Botfather](https://telegram.me/botfather)

Launch DateLunchBot from the command line by using the following command:
```
python datelunchbot.py -t ***YOUR TOKEN*** -f ***LOG FILENAME***
```
