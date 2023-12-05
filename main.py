#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 20:41:57 2022

@author: ert
"""

from apscheduler.schedulers.background import BackgroundScheduler

from schedules.yuncaijing import ycj_news_update
from schedules.eastmoney_future import eastmoney_future_update

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=ycj_news_update, trigger="interval", minutes=5)
    # scheduler.add_job(func=eastmoney_future_update, trigger="interval", minutes=5)
    scheduler.start()
    
    import time
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Shut down the scheduler gracefully
        scheduler.shutdown()
