#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 17:09:10 2021

@author: eee
"""

import requests

from config.static_vars import STOCK_HOST, DQN_HOST, BOT_DISPATCH_ADDRESS, IS_WHOLE_STOCK

def all_codes_receiver(is_train=not IS_WHOLE_STOCK):
    if is_train:
        api_suffix = 'all_training_codes'
    else:
        api_suffix = 'all_codes'
    r = requests.get(
        '{}/{}'.format(STOCK_HOST, api_suffix),
        timeout=10
    )
    # r.json() # actually it's a list.
    code_list = [c[0] for c in r.json()]
    return code_list


def all_open_days_receiver(start_date, end_date):
    r = requests.post(
        '{}/open_days'.format(DQN_HOST),
        json={'start_date': start_date, 'end_date': end_date},
        timeout=5
    )
    date_list = r.json()['dates']
    return date_list


def call_bot_dispatch(to, link, text):
    r = requests.post(
        BOT_DISPATCH_ADDRESS,
        data={
            'to': to,
            'link': link,
            'text': text
        },
        timeout=15
    )
    return r.json()
