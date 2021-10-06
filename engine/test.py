# -*- coding: utf-8 -*-
"""
Created on Sat Aug 28 08:42:27 2021

@author: ert
"""

import os

import torch
from torch.functional import F

from database.news_operator import newsDatabaseOperator
from config.static_vars import ROOT
from engine.brain import tokenizer, model, SCD
from utils.datetime_tools import date_range_generator


#### testing on training data ######
with open(os.path.join(ROOT, "negative.txt"), "r", encoding="utf-8") as f:
    n = f.read()
    neg_datasets = n.split("\n")  # purely because it's much less than positive

count = 0
error = 0
for idx, i in enumerate(neg_datasets):
    if idx % 100 == 0:
        print(idx)
    try:
        text = i.split("<|>")[0]
        label = i.split("<|>")[1]
    except:
        error += 1
        print(i)
        continue

    token_codes = tokenizer.encode_plus(text)
    with torch.no_grad():
        outputs = model(
            input_ids=torch.tensor([token_codes["input_ids"]]),
            token_type_ids=torch.tensor([token_codes["token_type_ids"]]),
        )

    base = F.softmax(outputs[0][0], dim=-1)
    index = base.argmax().item()
    prob = base.max().item()

    if index == int(label):
        count += 1
    # print(index, round(prob, 4))

print(count, len(neg_datasets), count / len(neg_datasets))

##### testing on non-training data #####
his_operator = newsDatabaseOperator()
insula = SCD(is_deploy=False)
source = "ycj"
dates = date_range_generator("2020-05-01", "2020-07-01")
neg_count, pos_count = 0, 0
total = 0
error = 0
for date in dates:
    print("testing non-training data", date)
    news = his_operator._get_news(source, date)
    total += len(news)
    for _id, content, codes in news:
        if not codes:
            continue

        roberta_index = insula.get_news_sentiment(content)
        if roberta_index > 0:  # positive
            label = 1
        elif roberta_index < 0:  # negative
            label = 0
        else:  # error
            error += 1
            continue

        token_codes = tokenizer.encode_plus(content)
        with torch.no_grad():
            outputs = model(
                input_ids=torch.tensor([token_codes["input_ids"]]),
                token_type_ids=torch.tensor([token_codes["token_type_ids"]]),
            )

        base = F.softmax(outputs[0][0], dim=-1)
        index = base.argmax().item()
        prob = base.max().item()

        if index < 0 and label == 0:
            neg_count += 1
        if index > 0 and label == 1:
            pos_count += 1

print("neg_count", neg_count, "pos_count", pos_count)
print((neg_count + pos_count) / (total - error))
