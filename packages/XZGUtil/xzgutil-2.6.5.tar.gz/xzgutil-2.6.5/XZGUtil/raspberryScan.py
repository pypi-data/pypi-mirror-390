#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021-01-12 17:38
# @Site    :
# @File    : raspberryScan.py
# @Software: PyCharm
"""获取本地ip"""
import socket
import threading
from XZGUtil.logger import conlog

# 创建互斥锁
lock = threading.Lock()



class MyThread(threading.Thread):  # MyThread类继承threading.Thread类
    def __init__(self, func, args1=None, args2=None):
        threading.Thread.__init__(self)
        self.func = func
        self.args1 = args1
        self.args2 = args2

    def run(self):  # t.start()语句调用run方法
        self.result = self.func(self.args1, self.args2)

    def getResult(self):  # getResult方法可获得func函数return的结果
        threading.Thread.join(self)
        return self.result

def get_host_ip():
    """
    查询本机ip地址
    :return:
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

# 定义查询路由函数
def search_routers(pt = "22"):
    # 设置需要扫描的端口号列表
    port_list = [pt]
    routers = []
    # 创建接收路由列表
    # 获取本地ip地址列表
    local_ips = socket.gethostbyname_ex(socket.gethostname())[2]
    # conlog(local_ips)
    # 存放线程列表池
    all_threads = []
    # 循环本地网卡IP列表
    for ip in local_ips:
        for i in range(1, 255):
            # 把网卡IP"."进行分割,生成每一个可用地址的列表
            array = ip.split('.')
            # 获取分割后的第四位数字，生成该网段所有可用IP地址
            array[3] = str(i)
            # 把分割后的每一可用地址列表，用"."连接起来，生成新的ip
            new_ip = '.'.join(array)
            # conlog(new_ip)
            # 遍历需要扫描的端口号列表
            for port in port_list:
                dst_port = int(port)
                # 循环创建线程去链接该地址
                t = MyThread(check_ip, new_ip, dst_port)
                t.start()
                # 把新建的线程放到线程池
                all_threads.append(t)
    # 循环阻塞主线程，等待每一字子线程执行完，程序再退出
    for t in all_threads:
        t.join()
    for value in all_threads:
        if value.getResult():
            routers += value.getResult()
    return routers


# 创建访问IP列表方法
def check_ip(new_ip, port):
    routers = []
    # 创建TCP套接字，链接新的ip列表
    scan_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 设置链接超时时间
    scan_link.settimeout(2)
    # 链接地址(通过指定我们 构造的主机地址，和扫描指定端口)
    result = scan_link.connect_ex((new_ip, port))
    #
    scan_link.close()
    # conlog(result)
    # 判断链接结果
    if result == 0:
        # 加锁
        lock.acquire()
        conlog(new_ip, '\t\t端口号%s开放' % port)
        routers.append((new_ip, port))
        # 释放锁
        lock.release()
    return routers


def serch_smp_ip():
    """查询树莓派IP"""
    l1 = search_routers()
    conlog("l1", l1)
    input("请关闭树莓派后，回车")
    l2 = search_routers()
    conlog("l2", l2)
    for i in l1:
        if i not in l2:
            conlog("树莓派ip为：", i)


if __name__ == '__main__':
    # 启动扫描程序
    serch_smp_ip()
