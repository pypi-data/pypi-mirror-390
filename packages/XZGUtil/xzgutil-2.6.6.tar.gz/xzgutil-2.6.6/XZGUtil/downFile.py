#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2022-11-08 14:07
# @Site    :
# @File    : downFile.py
# @Software: PyCharm
"""
下载文件
"""
import os
import requests
from XZGUtil.logger import conlog
from retrying import retry
from faker import Faker
from tqdm import tqdm
from pathlib import Path

faker = Faker()


def check_folder(path):
    """检查文件夹是否存在，不存在则创建"""
    try:
        # 优先使用pathlib
        dir_path = Path(path).resolve()  # 解析绝对路径[2,7](@ref)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"成功创建目录：{dir_path}")
        return str(dir_path)
    except Exception as e:
        print(f"目录创建失败：{e}")


def dl_file(name: str, type: str, save_path: str, url: str, cookie=None, header=None, data=None, params=None, method='GET', check: int = 13, stream=False):
    """
    发送请求
    :param name:  文件名
    :param type:  文件类型 ： jpg/gif/excel/xls
    :param save_path:  文件保存路径
    :param url:   下载地址
    :param cookie:  登录信息，str类型
    :param header:  请求头
    :param data:
    :param params:
    :param method:
    :param check:如果传递此参数，图片小于这个值将会重试
    :return:
    """
    check_folder(save_path)  # 检查文件夹是否存在，不存在则创建
    if header == None:
        header = {'cache-control': 'max-age=0',
                  'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
                  'sec-ch-ua-mobile': '?0',
                  'sec-ch-ua-platform': '"Windows"',
                  'upgrade-insecure-requests': '1',
                  'user-agent': faker.user_agent(),
                  'accept-language': 'zh-CN,zh;q=0.9'}
    if cookie:
        header['cookie'] = deal_cookie(cookie) if isinstance(cookie, dict) else cookie
    res = __send_req(data, params, method, url, header, stream)
    if stream:  # 数据流模式
        res.raise_for_status()  # 自动处理 HTTP 错误
        # 获取文件总大小
        total_size = int(res.headers.get('content-length', 0))
        if total_size == 0:
            conlog("⚠️服务器未提供文件大小。")
        # 下载并写入文件
        with open(f'{save_path}{name}.{type}', 'wb') as f:
            with tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    desc=f"下载中 {os.path.basename(save_path)}",
                    miniters=1  # 强制频繁刷新进度
            ) as pbar:
                for chunk in res.iter_content(8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
    else:
        if len(res.text) < check:
            assert False, "文件下载失败，下载大小小于给定值"
        conlog(f'开始下载文件：{name}，大小：{len(res.text)}')
        with open(f'{save_path}{name}.{type}', 'wb') as w:
            w.write(res.content)
    state = check_file_isexist_local(f'{name}.{type}', save_path)
    return state


def check_file_isexist_local(file_name, path):
    """检查文件是否存在"""
    isexist = os.path.exists(os.path.join(path, f"{file_name}"))
    return isexist


def deal_cookie(cookie: dict):
    """如果cookie是字段则转换成字符串"""
    cook = ''
    for key in cookie.keys():
        cook += f"{key}={cookie.get(key)};"
    return cook


@retry(stop_max_attempt_number=2)
def __send_req(data, params, method, url, header, stream):
    """发送请求"""
    if data and params:
        res = requests.request(method=method, url=url, headers=header, params=params, data=data, allow_redirects=False, stream=stream)
    elif data:
        res = requests.request(method=method, url=url, headers=header, data=data, allow_redirects=False, stream=stream)
    elif params:
        res = requests.request(method=method, url=url, headers=header, params=params, allow_redirects=False, stream=stream)
    else:
        res = requests.request(method=method, url=url, headers=header, allow_redirects=False, stream=stream)
    return res


if __name__ == '__main__':
    cookies = {
        'cookie2': '153b66f327e4a84588827d87e362420e',
        't': '2dbf516f1e4174f6301fc16425f7acf7',
        '_samesite_flag_': 'true',
        'thw': 'cn',
        'useNativeIM': 'false',
        'liveplatform_time': '1665199724',
        'c_csrf': 'f5596684-505f-4e13-8fc9-eac24d3905c3',
        '_tb_token_': '53635b757daf6',
        'linezing_session': 'DYOPFWkaaWk4ST6RsHoiqjZe_1667471922194zS92_4',
        'wwUserTip': 'false',
        'enc': 'BwMz5bgnk6%2FjjbUIfzKc18KejS4RAi%2BPitugMeearZBywO3XWfOZQD%2Bae%2FHT44n0EZpp%2FTMXNWHugUyJaCctng%3D%3D',
        'xlly_s': '1',
        '_m_h5_tk': '0787b72ad045c3a4854eb78b677f2afa_1667796014752',
        '_m_h5_tk_enc': '738d378f0ca57d775553db57f581936d',
        'unb': '2201448128180',
        'sn': 'minichinstudio%3A%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%901',
        'cancelledSubSites': 'empty',
        'sgcookie': 'E100HdiaOL9sF7ZOW6Blj1Vax1Fs92GN5t77FLZzayrWWGgXmZKLu0XuxtHjCbUd0AqwvIrcziXysjlAg8YSIWWQL6sjYWJ7iVMyEtDR5R8jSDg%3D',
        'uc1': 'cookie14=UoeyCUk8oCDImg%3D%3D&cookie21=VT5L2FSpdiBh',
        'csg': 'b58e9ad4',
        'skt': 'fecf6c98aaeeda85',
        '_cc_': 'VFC%2FuZ9ajQ%3D%3D',
        'cna': 'ummxG79MLz0CAXPuK+L/d08v',
        'l': 'eB__VCsmTbNS1NELKO5ahurza77OWhAXHsPzaNbMiIncI68-rFH6V1rsMoxSqpeF5HG5-tfXLexPUcfRbde28lULRxO4E54AKEtD20p6-',
        'tfstk': 'cYeAIZsD7ab0cuQiUxCobYfAUkW5Z_RlW4tjSdeKNN5HrEvwSF5DTJ2pJlfjf2uA2',
        'isg': 'BB4eGegr8SF6FiVtEY3RMP30b7Rg3-JZnx7ltMizCmma65DFMm6facrJ4_dnU9px',
    }
    params = {
        'rptDataContentType': 'adv',
        'bizCode': 'dkx',
        'unifyType': 'zhai',
        'effectType': 'click',
        'groupByDate': 'day',
        'effects': '15',
        'startTime': '2022-11-06',
        'endTime': '2022-11-06',
        'timeStr': '1667817662888',
        'dynamicToken': '212228220196224224212192432388216440428444464428',
        'csrfID': '166781597169901799290112116015634',
        'webOpSessionId': '38hz55p9rco',
    }

    url = 'https://adbrain.taobao.com/api/export/report/exportOverProductReportList.json'
    dl_file(name="测试1", type='xls', save_path='./', url=url, cookie=cookies, params=params)
