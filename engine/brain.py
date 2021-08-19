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
        self.weight_decay = 1

    def get_news_sentiment(self, news_str):
        try:
            results = self.insula(news_str)[0]
            negative_index = -1 if results['label'] == 'negative' else 1
            sentimental_index = results['score']*negative_index
        except:
            sentimental_index = 0  # sometimes it's just throw an error

        return round(sentimental_index * self.weight_decay, 4)
