#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 10:16:58 2021

@author: eee
"""
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""




from fastapi import FastAPI
from pydantic import BaseModel
from config.static_vars import API_PREFIX
class historicalWeightPost(BaseModel):
    start_date: str
    end_date: str


app = FastAPI()


@app.get("/{}/live_weight".format(API_PREFIX))
def call_live_weight():
    results = {'sh.600006': 0.94}
    print('hello madafaka')
    return results


@app.post("/{}/historical_weight".format(API_PREFIX))
def call_historical_weight(item: historicalWeightPost):
    start_date = item.start_date
    end_date = item.end_date
    print(start_date, end_date)
    fields = [start_date, end_date]
    fetched = [[1, 2], [4, 5]]
    results = list()
    for f in fetched:
        results.append(dict(zip(fields, f)))
    return {'results': results}
