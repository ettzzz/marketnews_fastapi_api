# -*- coding: utf-8 -*-

import os

MONGO_URI = os.getenv("AZURE_MONGO_URI")
DB_NAME = "offline_news"
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
IS_DEBUG= os.getenv("DEBUG")

if IS_DEBUG == "0":
    IS_DEBUG = False
else:
    IS_DEBUG = True

# web service
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"

# project exclusive
DAY_ZERO = "2019-01-01"
