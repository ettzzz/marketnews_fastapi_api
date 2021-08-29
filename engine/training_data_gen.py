# -*- coding: utf-8 -*-
"""
Created on Sat Aug 28 09:37:55 2021

@author: ert
"""

import os

from database.news_operator import newsDatabaseOperator
from utils.datetime_tools import date_range_generator
from engine.brain import SCD
from config.static_vars import ROOT

'''
local latest news 8.24 14:55 ~120,000 data
label 0: negative, 1: positive
'''

his_operator = newsDatabaseOperator()
insula = SCD(is_deploy=False) # make sure insula is using roberta model to ensure accuracy
source = 'ycj'


def generate_train_dataset(date_start='2021-01-01', date_end='2021-08-23'):
    '''
    Parameters
    ----------
    date_start : TYPE, optional
        DESCRIPTION. The default is '2021-01-01'.
    date_end : TYPE, optional
        DESCRIPTION. The default is '2021-08-23'.

    Returns 
    -------
    None. But will generate 2 txt files under /models

    '''
    dates = date_range_generator(date_start, date_end)
    neg_count, pos_count = 0, 0
    for date in dates:
        print('generating training data for', date)
        news = his_operator._get_news(source, date)
        neg = open(os.path.join(ROOT, 'models', 'negative.txt'), 'a', encoding='utf-8')
        pos = open(os.path.join(ROOT, 'models', 'positive.txt'), 'a', encoding='utf-8')
            
        for _id, content, codes in news:
            if not codes:
                continue
            index = insula.get_news_sentiment(content)
            if abs(index) < 0.8: # get rid of neutral contents
                continue
            
            if index < 0:
                neg.write('<|>'.join([content, '0', '\n']))
                neg_count += 1
            else:
                pos.write('<|>'.join([content, '1', '\n']))
                pos_count += 1
                
        neg.close()
        pos.close()
    
    print('neg_count', neg_count, 'pos_count', pos_count)