#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2023-08-23 18:28
# @Site    :
# @File    : quickTooling.py
# @Software: PyCharm
"""
小工具
"""


def split_list(lst, size):
    """
    列表切片
    :param lst:  [1, 1, 16, 85, 9, 2, 33, 4]
    :param size: 2
    :return: [[1, 1], [16, 85], [9, 2], [33, 4]]
    """
    divided_list = []
    for i in range(0, len(lst), size):
        divided_list.append(lst[i:i + size])
    return divided_list


def remove_duplicates(lst):
    """
    列表元素去重，里面元素类型不限
    :param lst:
    :return:
    """
    unique_list = []
    seen = set()
    for item in lst:
        if isinstance(item, (list, tuple, dict)):
            item = str(item)  # 转换为字符串，以处理字典和列表的哈希问题
        if item not in seen:
            unique_list.append(item)
            seen.add(item)
    return unique_list

def sort_list(lst):
    """
    列表元素排序
    :param lst:
    :return:
    """
    sorted_lst = sorted(lst, key=lambda x: str(x))
    return sorted_lst

if __name__ == '__main__':
    lst = [1, 1, 16, 85, 9, 2, 33, 4]
    size = 3
    print(split_list(lst, size))
