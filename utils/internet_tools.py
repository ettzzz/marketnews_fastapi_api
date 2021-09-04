#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 17:09:10 2021

@author: eee
"""

import requests

from config.static_vars import STOCK_HOST, DQN_HOST, BOT_DISPATCH_ADDRESS

def all_codes_receiver(is_train=True):
    if is_train:
        api_suffix = 'all_training_codes'
    else:
        api_suffix = 'all_codes'
    r = requests.get(
        '{}/{}'.format(STOCK_HOST, api_suffix),
        timeout=15
    )
    # r.json() # actually it's a list.
    code_list = [c[0] for c in r.json()]
    return code_list


def all_open_days_receiver():
    r = requests.get(
        '{}/open_days'.format(DQN_HOST),
        timeout=15
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
        }
    )
    return r.json()
