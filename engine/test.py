# -*- coding: utf-8 -*-
"""
Created on Sat Aug 28 08:42:27 2021

@author: ert
"""
import torch
from torch.functional import F
from transformers import AutoTokenizer, AutoConfig
from transformers import AutoModelForSequenceClassification

import os
from config.static_vars import ROOT

albert_path = os.path.join(ROOT, 'models', 'trained')
tokenizer = AutoTokenizer.from_pretrained(albert_path)
model_config = AutoConfig.from_pretrained(albert_path)
model_config.num_labels = 2
model_config.id2label = {
    "0": "negative",
    "1": "positive"
  }
model_config.label2id = {
    "negative": "0",
    "positive": "1"
  }
cls_model = AutoModelForSequenceClassification.from_pretrained(albert_path, config=model_config)

cls_model.eval()



#### testing on training data ######
neg = open(os.path.join(ROOT, 'negative.txt'), 'r', encoding='utf-8')
n = neg.read()
neg.close()


count = 0
error = 0
neg_datasets = n.split('\n')
for idx, i in enumerate(neg_datasets):
    if idx % 100 == 0:
        print(idx)
    try:
        text = i.split('<|>')[0]
        label = i.split('<|>')[1]
    except:
        error += 1
        print(i)
        continue
    
    token_codes = tokenizer.encode_plus(text)
    
    with torch.no_grad():
        outputs = cls_model(
            input_ids=torch.tensor([token_codes['input_ids']]),
            token_type_ids = torch.tensor([token_codes['token_type_ids']])
            )
    
    base = F.softmax(outputs[0][0], dim=-1)
    index = base.argmax().item()
    prob = base.max().item()
    
    if index == int(label):
        count += 1
    # print(index, round(prob, 4))

print(count, len(neg_datasets), count/len(neg_datasets))

##### testing on non-training data #####
source = 'ycj'
dates = date_range_generator('2020-05-01', '2020-07-01')
neg_count, pos_count = 0, 0
total = 0
for date in dates:
    print('generating', date)
    news = his_operator._get_news(source, date)
    total += len(news)
    for _id, content, codes in news:
        if not codes:
            continue
        
        index = insula.get_news_sentiment(content)
        
        token_codes = tokenizer.encode_plus(content)
        with torch.no_grad():
            outputs = cls_model(
                input_ids=torch.tensor([token_codes['input_ids']]),
                token_type_ids = torch.tensor([token_codes['token_type_ids']])
                )
        
        base = F.softmax(outputs[0][0], dim=-1)
        index = base.argmax().item()
        prob = base.max().item()

        if index < 0 and int(index) == 0:
            neg_count += 1
        if index > 0 and int(index) == 1:
            pos_count += 1

print('neg_count', neg_count, 'pos_count', pos_count)
print((neg_count+pos_count)/total)
