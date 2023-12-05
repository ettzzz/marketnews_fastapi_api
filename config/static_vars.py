# -*- coding: utf-8 -*-

import os

USERNAME = 'news_reporter'
PASSWORD = os.getenv("MONGO_NEWS_PASSWORD")
DB_NAME = 'offline_news'

HOSTNAME = '127.0.0.1'
PORT = 3717
MONGO_URI = f'mongodb://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/?authSource={DB_NAME}&authMechanism=SCRAM-SHA-1'

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DEBUG= os.getenv("_DEPLOY") is None

# web service
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"

# project exclusive
DAY_ZERO = "2019-01-01"
