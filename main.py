# -*- coding: utf-8 -*-

from fastapi import FastAPI

from config.static_vars import API_PREFIX
from scheduler.schedule_maker import watcher, his_operator

app = FastAPI()


@app.get("/{}/live_weight".format(API_PREFIX))
def call_live_weight():
    results = watcher.get_code_weight()
    return results


@app.get("/{}/historical_weight".format(API_PREFIX))
def call_historical_weight():
    # POST?
    # TODO:his_operator.get_historical_weight
    pass
