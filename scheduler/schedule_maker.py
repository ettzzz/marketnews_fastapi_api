# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 20:56:12 2021

@author: ert
"""


from database.news_operator import newsDatabaseOperator



from scraper._sina import sinaScrapper
ss = sinaScrapper()

his_operator = newsDatabaseOperator()


