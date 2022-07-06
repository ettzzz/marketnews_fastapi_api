#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 20:41:57 2022

@author: ert
"""

from apscheduler.schedulers.background import BackgroundScheduler

from schedules import call_for_update


def main():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=call_for_update, trigger="interval", minutes=5)
    scheduler.start()


if __name__ == "__main__":
    # main()
    call_for_update()
    """
    if main() is not on the run, add
        */5 * * * * /path/to/python3 /path/to/project/main.py
    to crontab -e
    which means run this script every 5 minutes
    """
