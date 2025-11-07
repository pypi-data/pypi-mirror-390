#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2022-11-07 13:30
# @Site    :
# @File    : updateSpider.py
# @Software: PyCharm
"""
爬虫更新时间记录
"""
import datetime
import os
from backports import configparser2 as configparser  # 这个用于读取文件，写入文件会将中文注释删除
from XZGUtil.logger import conlog
from XZGUtil.timeUtil import get_now_date, getdate



class upconfig(object):
    def __init__(self, path, file_name="update", update_tag='spiderState'):
        """
        :param file_name:  文件名
        :param update_tag:   标签名
        """
        self.updatePath = os.path.join(path, f"{file_name}.ini")
        self.config = configparser.RawConfigParser()
        # with open(self.updatePath, encoding="utf-8-sig") as f:
        #     self.config.read_file(f)
        self.update_tag = update_tag

    def get_information(self, name):
        """
        获取更新日期
        :param name:
        :return:
        """
        try:
            with open(self.updatePath, encoding="utf-8-sig") as f:
                self.config.read_file(f)
            data = self.config.get(self.update_tag, f'{name}')
        except:
            data = None
        return data

    def set_information(self, name, date=get_now_date()):
        """
        修改更新日期配置文件
        :param name: 标签下的具体类名
        :return:
        """
        try:
            self.config.set(self.update_tag, f'{name}', date)
        except configparser.NoSectionError:
            with open(self.updatePath, 'a') as f:
                f.write(f"[{self.update_tag}]")
            self.config.read(self.updatePath, encoding="utf-8-sig")
            self.config.set(self.update_tag, f'{name}', date)
        self.config.write(open(self.updatePath, 'w', encoding='utf-8-sig'))
        conlog(f'{self.update_tag}   *   {name}  *   ', f"更新完成_{date} ")

    def check_update(self, name, difference: int = 0):
        """
        检查今日是否更新
        :param name: 检查对象
        :param difference: 时间对比基准点，默认为0（今日），如果为 difference=1 则代表：如果上次更新日期是前一天，则返回False，代表更新完成，不需要更新
        :return:
        """
        try:
            with open(self.updatePath, encoding="utf-8-sig") as f:
                self.config.read_file(f)
            value = self.config.get(self.update_tag, f'{name}')
        except:
            try:
                self.config.set(self.update_tag, f'{name}', getdate(1))  # 如果报错说明没有这个则需要创建一个，并赋值为前一日
            except configparser.NoSectionError:
                with open(self.updatePath, 'a') as f:
                    f.write(f"[{self.update_tag}]")
                self.config.read(self.updatePath, encoding="utf-8-sig")
                self.config.set(self.update_tag, f'{name}', getdate(1))
            self.config.write(open(self.updatePath, 'w', encoding='utf-8-sig'))
            value = self.config.get(self.update_tag, f'{name}')
        if value == getdate(difference):
            conlog(f'{name}', "今日已更新完成")
            return False
        else:
            return True


