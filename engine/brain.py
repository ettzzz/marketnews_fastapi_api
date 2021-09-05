#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 14:30:38 2021

@author: eee
"""
import os

import torch
from torch.functional import F
from transformers import pipeline
from transformers import AutoTokenizer, AutoConfig, AutoModelForSequenceClassification

from config.static_vars import ROBERTA_CONFIG, ROOT

device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

id_label_mapping = {
  "0": "negative",
  "1": "positive"
}

def _init_lite_albert():
    albert_path = os.path.join(ROOT, 'models', 'trained')
    tokenizer = AutoTokenizer.from_pretrained(albert_path)
    config = AutoConfig.from_pretrained(albert_path)
    
    config.num_labels = len(id_label_mapping)
    config.id2label = id_label_mapping
    config.label2id = {v: k for k, v in id_label_mapping.items()}
    
    model = AutoModelForSequenceClassification.from_pretrained(
        albert_path, 
        config=config
        )
    # model.eval()
    model.to(device)
    
    return tokenizer, model


tokenizer, model = _init_lite_albert()


class SCD():
    '''
    sentiment control dispatch
    '''

    def __init__(self, is_deploy=True):
        if is_deploy:
            self.insula = self._lite_pipeline
        else:
            self.insula = pipeline(**ROBERTA_CONFIG)
            
    def _lite_pipeline(self, news_str):
        token_codes = tokenizer.encode_plus(news_str)
        with torch.no_grad():
            outputs = model(
                input_ids=torch.tensor([token_codes['input_ids']]).to(device),
                token_type_ids = torch.tensor([token_codes['token_type_ids']]).to(device)
                )
        base = F.softmax(outputs[0][0], dim=-1)
        index = base.argmax().item()
        prob = base.max().item()
        
        return [{
            'label': id_label_mapping[str(index)],
            'score': prob
            }]

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
