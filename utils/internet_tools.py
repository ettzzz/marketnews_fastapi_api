#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 17:09:10 2021

@author: eee
"""

import requests

from config.static_vars import BOT_DISPATCH_ADDRESS


def call_bot_dispatch(to, link, text):
    r = requests.post(
        BOT_DISPATCH_ADDRESS, data={"to": to, "link": link, "text": text}, timeout=15
    )
    return r.json()
