#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 16:40:16 2021

@author: eee
"""

'''
日期范围
初始化weights都是0 先用一个月的做启动吧 以后就得从2019-02-01开始了

每天先从sql读出来
分时段每个时段来一个计算一次weight_dict
储存一条
每天结束的时候decay一个


'''
