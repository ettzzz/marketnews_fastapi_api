# -*- coding: utf-8 -*-

from fastapi import FastAPI
from pydantic import BaseModel

from config.static_vars import API_PREFIX, DEBUG
from scheduler.schedule_maker import watcher, his_operator


class historicalWeightPost(BaseModel):
    start_date: str
    end_date: str

class trainWeightPost(BaseModel):
    start_date: str
    end_date: str
    code: str

class poolNewsFeaturePost(BaseModel):
    pass

app = FastAPI(debug=DEBUG)

@app.get("/{}/live_weight".format(API_PREFIX))
def call_live_weight():
    results = watcher.get_code_weight()
    return results


@app.post("/{}/historical_weight".format(API_PREFIX))
def call_historical_weight(item: historicalWeightPost):
    start_date = item.start_date
    end_date = item.end_date
    results_list = his_operator.get_feature_weights(start_date, end_date)
    return {'results': results_list}


@app.post("/{}/train_weight".format(API_PREFIX))
def call_train_weight(item: trainWeightPost):
    code = item.code
    start_date = item.start_date
    end_date = item.end_date
    results_dict = his_operator.get_code_weights(code, start_date, end_date)
    return {'results': results_dict}

# @app.post("/{}/pool_news_feature".format(API_PREFIX))
# def call_pool_news_feature(poolNewsFeaturePost):
#     return
