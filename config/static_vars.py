# -*- coding: utf-8 -*-

import os
import platform

from config.local_secrets import MTB_DOMAIN, MONGO_URI, DB_NAME

# deployment
OS = platform.system()
OS_VER = platform.version()
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

if "Debian" in OS_VER:
    IS_DEBUG = False
else:
    IS_DEBUG = True

# web service
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
BOT_DISPATCH_ADDRESS = f"http://{MTB_DOMAIN}/tgbot/send_message"

# project exclusive
DAY_ZERO = "2019-01-01"
DAILY_TICKS = [
    "00:00:00",
    "10:00:00",
    "10:30:00",
    "11:00:00",
    "11:30:00",
    "13:30:00",
    "14:00:00",
    "14:30:00",
    "15:00:00",
    "23:59:59",
]
