'''
Created on Jul 11, 2023
@author: scanlom
'''

from datetime import date
from datetime import datetime
from datetime import timedelta

def convert_date( json ):
    return datetime.strptime(json['date'][:10], '%Y-%m-%d')

def get_ytd_base_date():
    day = datetime.today()
    if day.month == 1 and day.day == 1:
        return date(day.year-1, 1, 1)
    return date(day.year, 1, 1)

def get_qtd_base_date():
    day = datetime.today()
    if day.month > 9 and not (day.month == 10 and day.day == 1):
        return date(day.year, 10, 1)
    elif day.month > 6 and not (day.month == 7 and day.day == 1):
        return date(day.year, 7, 1)
    elif day.month > 3 and not (day.month == 4 and day.day == 1):
        return date(day.year, 4, 1)
    elif not (day.month == 1 and day.day == 1):
        return date(day.year, 1, 1)
    return date(day.year - 1, 10, 1)

def get_day_base_date():
    yesterday = datetime.today() - timedelta(1)
    return date(yesterday.year, yesterday.month, yesterday.day)