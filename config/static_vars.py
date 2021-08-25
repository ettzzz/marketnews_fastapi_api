# -*- coding: utf-8 -*-

import os
import platform

import torch


OS = platform.system()
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

if OS == 'Linux':
    ICU_IP = 'localhost'
    DEBUG = False
else:
    ICU_IP = '82.157.178.246'
    DEBUG = True

NEWS_HISTORY_PATH = os.path.join(ROOT, 'trade_news.db')
DAY_ZERO = '2019-01-01'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'
MTB_IP = 'https://api.ettzzz.nl'
BOT_DISPATCH_ADDRESS = '{}/api_v1/send_message'.format(MTB_IP)
API_PREFIX = 'api_v1'


STOCK_HOST = 'http://{}:7702/api_v1'.format(ICU_IP)
DQN_HOST = 'http://{}:7704/api_v1'.format(ICU_IP)
SENTI_REDIS_CONFIG = {
    'host': ICU_IP,
    'port': 7779,
    'db': 1,
    'password': 'fuzademima',
    'charset': 'utf-8',
    'decode_responses': True
}


HAS_CUDA = torch.cuda.is_available()
HUGGING_CONFIG = {
    'task': 'sentiment-analysis',
    'model': 'liam168/c2-roberta-base-finetuned-dianping-chinese',
    'device': 0 if HAS_CUDA else -1  # default -1 as cpu, other 01234 refer to gpu number
}

DAILY_TICKS = [
    '00:00:00',
    '10:00:00', '10:30:00', '11:00:00', '11:30:00',
    '13:30:00', '14:00:00', '14:30:00', '15:00:00',
    '23:59:59'
]
