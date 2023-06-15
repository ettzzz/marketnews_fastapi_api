#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 20:41:57 2022

@author: ert
"""

from apscheduler.schedulers.background import BackgroundScheduler

from schedules.yuncaijing import ycj_news_update
from schedules.eastmoney_future import eastmoney_future_update


def main():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=ycj_news_update, trigger="interval", minutes=5)
    scheduler.add_job(func=eastmoney_future_update, trigger="interval", minutes=5)
    scheduler.start()
    ## this is better for a very short interval schedule, e.g. less than 1 minute that crontab cannot handle


if __name__ == "__main__":
    main()
    """
    if main() is not on the run, add
        */5 * * * * /path/to/python3 /path/to/project/main.py
    to crontab -e
    which means run this script every 5 minutes
    """
