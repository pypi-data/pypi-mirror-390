#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2023-03-10 16:43
# @Site    :
# @File    : timer.py
# @Software: PyCharm
"""定时器"""

import subprocess
from datetime import datetime as dd, time as dt
import time
from XZGUtil.logger import conlog


def time_slot(st:str,et:str,fun):
    """时段定时器，在给定的时间段内每日循环运行指定函数"""
    DAY_START = dt(9, 28)
    DAY_END = dt(9, 30)
    while True:
        current_time = dd.now().time()
        if DAY_START <= current_time <= DAY_END:
            # 判断时候在可运行时间内
            try:
                cmd = 'python tbLiveSpider.py'
                p = subprocess.Popen(cmd, shell=True)
                p.wait()
            except:
                pass
        conlog('wait..........')
        time.sleep(10)


