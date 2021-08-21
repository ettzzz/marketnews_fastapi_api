#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 14:30:38 2021

@author: eee
"""

from transformers import pipeline

from config.static_vars import HUGGING_CONFIG


class SCD():
    '''
    sentiment control dispatch
    preliminary performance estimation: 0.35s inference time, 0.8 accuracy
    '''

    def __init__(self):
        self.insula = pipeline(**HUGGING_CONFIG)

    def weight_mapping(self, weight_score):
        '''
        weight_score: -1~1
        '''
        x = weight_score
        if x > 0:
            return round(1-(1-x)*2, 2)
        elif x < 0:
            return round(-1+(1+x)*2, 2)
        else:
            return 0

    def weight_decay(self, weight_score, decay_count):
        decay = round(weight_score * (0.7**decay_count), 2)
        if abs(decay) < 0.1:
            return 0
        else:
            return decay

    def get_news_sentiment(self, news_str, is_mapping=True):
        try:
            results = self.insula(news_str)[0]
            negative_index = -1 if results['label'] == 'negative' else 1
            sentimental_index = results['score']*negative_index
        except:
            sentimental_index = 0  # sometimes it's just throw an error

        if is_mapping:
            return self.weight_mapping(sentimental_index)
        else:
            return round(sentimental_index, 2)
