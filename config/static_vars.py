# -*- coding: utf-8 -*-

import os
import platform

import torch

# deployment
OS = platform.system()
OS_VER = platform.version()
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
MTB_IP = 'http://www.ettzzz.ga'
if 'Debian' in OS_VER:
    ICU_IP = 'localhost'
    DEBUG = False
else:
    ICU_IP = '82.157.178.246'
    DEBUG = True

# project exclusive
IS_WHOLE_STOCK = True
DAY_ZERO = '2019-01-01'
NEWS_HISTORY_PATH = os.path.join(ROOT, 'trade_news.db')
DAILY_TICKS = [
    '00:00:00',
    '10:00:00', '10:30:00', '11:00:00', '11:30:00',
    '13:30:00', '14:00:00', '14:30:00', '15:00:00',
    '23:59:59'
]
HAS_CUDA = torch.cuda.is_available()
DEVICE = 'cuda:0' if HAS_CUDA else 'cpu'
ROBERTA_CONFIG = {
    'task': 'sentiment-analysis',
    'model': 'liam168/c2-roberta-base-finetuned-dianping-chinese',
    'device': 0 if HAS_CUDA else -1  # default -1 as cpu, other 01234 refer to gpu number
}

# web service
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'
API_PREFIX = 'api_v1'
STOCK_HOST = 'http://{}:7702/api_v1'.format(ICU_IP)
DQN_HOST = 'http://{}:7704/api_v1'.format(ICU_IP)
BOT_DISPATCH_ADDRESS = '{}/api_v1/send_message'.format(MTB_IP)

SENTI_REDIS_CONFIG = {
    'host': ICU_IP,
    'port': 7779,
    'db': 1,
    'password': 'fuzademima',
    'charset': 'utf-8',
    'decode_responses': True
}

# logging
LOGGING_FMT = "%(asctime)s %(levelname)s %(funcName)s in %(filename)s: %(message)s"
LOGGING_DATE_FMT = "%Y-%m-%d %a %H:%M:%S"
LOGGING_NAME = 'jibberjabber'
