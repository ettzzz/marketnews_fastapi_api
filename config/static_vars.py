# -*- coding: utf-8 -*-

import os

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
NEWS_HISTORY_PATH = os.path.join(ROOT, 'trade_news.db')

DAY_ZERO = '2019-01-01'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'
MTB_IP = 'https://api.ettzzz.nl'
BOT_DISPATCH_ADDRESS = '{}/api_v1/send_message'.format(MTB_IP)
ICU_IP = '82.157.178.246'

SENTI_REDIS_CONFIG = {
    'host': ICU_IP,
    'port': 7779,
    'db': 1,
    'password': 'fuzademima',
    'charset': 'utf-8',
    'decode_responses': True
}


NEWS_ID_ZERO = {
    'sina': 1099379  # first news id on DAY_ZERO
}

HUGGING_CONFIG = {
    'task': 'sentiment-analysis',
    'model': 'liam168/c2-roberta-base-finetuned-dianping-chinese'
}
