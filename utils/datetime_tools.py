# -*- coding: utf-8 -*-

import time
import datetime

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATE_TIME_FORMAT = DATE_FORMAT + ' ' + TIME_FORMAT


def struct_timestr(timestr, _format=DATE_FORMAT):
    structed_time = time.strptime(timestr, _format)
    return structed_time


def struct_datestr(datestr, _format=DATE_FORMAT):
    structed_date = datetime.datetime.strptime(datestr, _format)
    return structed_date


def get_now():
    return round(time.time())


def get_today_date():
    today = datetime.datetime.now()
    today_str = datetime.datetime.strftime(today, DATE_FORMAT)
    return today_str


def get_delta_date(date, days):
    # type(date) is str
    # type(target_datestr) is str
    strd = struct_datestr(date)
    target_strd = strd + datetime.timedelta(days)
    target_datestr = datetime.datetime.strftime(target_strd, DATE_FORMAT)
    return target_datestr


def timestamper(time_str, _format=DATE_FORMAT):
    '''
    time_in_str: '2016-05-27 07:07:26'
    _format: '%Y-%m-%d %H:%M:%S'
    return 1464304046
    '''
    if _format is int:
        return int(time_str)
    else:
        structed_time = struct_timestr(time_str, _format)
        return int(time.mktime(structed_time))


def reverse_timestamper(ten_digit_str, _format=DATE_TIME_FORMAT):
    structed_time = time.localtime(int(ten_digit_str))
    time_str = time.strftime(_format, structed_time)
    return time_str


def date_range_generator(start, end, step=1,
                         format_=DATE_FORMAT,
                         category='all',
                         is_reverse=False):
    strptime = datetime.datetime.strptime
    strftime = datetime.datetime.strftime
    end = strftime(strptime(end, format_) + datetime.timedelta(1), format_)
    days = (strptime(end, format_) - strptime(start, format_)).days

    if is_reverse:
        ranger = range(0, days, step)[::-1]
    else:
        ranger = range(0, days, step)

    for i in ranger:
        new_day = strptime(start, format_) + datetime.timedelta(i)
        # dates = []
        if category == 'all':
            yield strftime(new_day, format_)
        elif category == 'weekend':
            if new_day.weekday() > 4:
                yield strftime(new_day, format_)
        else:
            if new_day.weekday() <= 4:
                yield strftime(new_day, format_)
