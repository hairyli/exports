#!/usr/bin/env python3
import os
import time
import sys
import datetime
import socket  # 获取主机名
import psutil  # 获取CPU等信息
import re
from prometheus_client import Gauge,start_http_server, pushadd_to_gateway, CollectorRegistry

# 以下是变量值
CPUT = 2  # 计算CPU利用率的时间间隔
NETT = 2  # 计算网卡流量的时间间隔
LOOPT = 2  # 脚本循环时间间隔


# 获取系统基本信息
def baseinfo():
    hostname = socket.gethostname()
    host_ip = socket.gethostbyname(socket.getfqdn(socket.gethostname()))
    user_conn = len(psutil.users())
    start_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    sys_runtime = os.popen('w').readline().split('users')[0].split('up')[1].strip()[:-1].strip()[:-1]
    process = os.popen('ps -ef |wc -l').read().split()[0]
    return {"hostname": hostname, "user_conn": user_conn, "sys_start_time": start_time, "now_time": now_time,
            "sys_runtime": sys_runtime, "process": process}


# 获取CPU信息
def cpuinfo():
    ave_load = os.popen('uptime').readline().split(":")[-1].split()
    ave_load = ' '.join(ave_load)  # CPU平均负载
    # 以下四项值都是获取的瞬时值
    user_time = psutil.cpu_times().user  # 用户态使用CPU时间
    sys_time = psutil.cpu_times().system  # 系统态使用CPU时间
    idle_time = psutil.cpu_times().idle  # CPU空闲时间
    iowait_time = psutil.cpu_times().iowait  # IO等待时间
    total_cpu = 0
    for i in range(len(psutil.cpu_times())):
        total_cpu += psutil.cpu_times()[i]
    user_use = str(round(user_time / total_cpu * 100, 2)) + '%'
    sys_use = str(round(sys_time / total_cpu * 100, 2)) + '%'
    idle = str(round(idle_time / total_cpu * 100, 2)) + '%'
    iowait = str(round(iowait_time / total_cpu * 100, 2)) + '%'
    cpu_pre = str(psutil.cpu_percent(CPUT)) + "%"
    logical_cpu = psutil.cpu_count()
    pyhsical_cpu = psutil.cpu_count(logical=False)


    return {
        "ave_load": ave_load,
        "user_use": user_use,
        "sys_use": sys_use,
        "idle": idle,
        "iowait": iowait,
        "cpu_pre": cpu_pre,
        "logical_cpu": logical_cpu,
        "pyhsical_cpu": pyhsical_cpu,

    }


# 获取内存信息
def meminfo():
    total_mem = str(round(psutil.virtual_memory().total / 1024 / 1024 / 1024)) + 'G'
    use_mem = str(round(psutil.virtual_memory().used / 1024 / 1024 / 1024)) + 'G'
    mem_percent = str(psutil.virtual_memory().percent) + '%'
    free_mem = str(round(psutil.virtual_memory().free / 1024 / 1024 / 1024)) + 'G'
    swap_mem = str(round(psutil.swap_memory().total / 1024 / 1024 / 1024)) + "G"
    swap_use = str(round(psutil.swap_memory().used / 1024 / 1024 / 1024)) + 'G'
    swap_free = str(round(psutil.swap_memory().free / 1024 / 1024 / 1024)) + 'G'
    swap_percent = str(psutil.swap_memory().percent) + '%'

    return {
        "total_mem": total_mem,
        "use_mem": use_mem,
        "free_mem": free_mem,
        "mem_percent": mem_percent,
        "swap_mem": swap_mem,
        "swap_use": swap_use,
        "swap_free": swap_free,
        "swap_percent": swap_percent,

    }


# 获取磁盘信息
def diskinfo():
    d1, d2, d3, d4, d5 = [], [], [], [], []
    disk_total, disk_used, disk_free = 0, 0, 0
    disk_len = len(psutil.disk_partitions())
    for info in range(disk_len):
        disk = psutil.disk_partitions()[info][1]
        if len(disk) < 10:
            d1.append(disk)
            total = str(round(psutil.disk_usage(disk).total / 1024 / 1024 / 1024)) + 'G'
            total_num = psutil.disk_usage(disk).total
            disk_total += total_num
            free = str(round(psutil.disk_usage(disk).free / 1024 / 1024 / 1024)) + 'G'
            disk_free += psutil.disk_usage(disk).free
            used = str(round(psutil.disk_usage(disk).used / 1024 / 1024 / 1024)) + 'G'
            disk_used += psutil.disk_usage(disk).used
            percent = str(psutil.disk_usage(disk).percent) + '%'
            d2.append(total)
            d3.append(free)
            d4.append(used)
            d5.append(percent)
    disk_used_percent = str(round(disk_used / disk_total * 100, 2)) + '%'
    disk_free_percent = str(round(disk_free / disk_total * 100, 2)) + '%'
    disk_total = str(round(disk_total / 1024 / 1024 / 1024)) + "G"
    disk_free = str(round(disk_free / 1024 / 1024 / 1024)) + "G"
    disk_used = str(round(disk_used / 1024 / 1024 / 1024)) + "G"
    return {
        "disk": [
            {"disk_total": disk_total},
            {"disk_free": disk_free},
            {"disk_used": disk_used},
            {"disk_used_percent": disk_used_percent},
            {"disk_free_percent": disk_free_percent}
        ],
        "partitions": [
            {"mount": (d1)},
            {"total": (d2)},
            {"free": (d3)},
            {"used": (d4)},
            {"percent": (d5)}
        ]
    }

if __name__ == '__main__':
    start_http_server(8007)
    registry = CollectorRegistry()
    g_baseinfo = Gauge('baseinfo_test_metric', 'Description of gauge', ['hostname', 'now_time', 'sys_runtime'])
    g_cpuinfo = Gauge('cpuinfo_test_metric', 'Description of gauge', ['user_use', 'cpu_pre', 'iowait'])
    g_meminfo = Gauge('meminfo_test_metric', 'Description of gauge', ['total_mem', 'use_mem', 'mem_percent'])
    g_diskinfo = Gauge('diskinfo_test_metric', 'Description of gauge', ['disk_total', 'disk_free'])
    while True:
        baseinfo_dict = baseinfo()
        cpuinfo_dict = cpuinfo()
        meminfo_dict = meminfo()
        diskinfo_dict = diskinfo()
        g_baseinfo.labels(hostname=baseinfo_dict['hostname'], now_time=baseinfo_dict['now_time'], sys_runtime=baseinfo_dict['sys_runtime'])
        g_cpuinfo.labels(user_use=cpuinfo_dict['user_use'], cpu_pre=cpuinfo_dict['cpu_pre'], iowait=cpuinfo_dict['iowait'])
        g_meminfo.labels(total_mem=meminfo_dict['total_mem'], use_mem=meminfo_dict['use_mem'], mem_percent=meminfo_dict['mem_percent'])
        g_diskinfo.labels(disk_total=diskinfo_dict['disk'][0]['disk_total'], disk_free=diskinfo_dict['disk'][1]['disk_free'])


        pushadd_to_gateway('192.168.217.137:9091', job='info_pushgateway', registry=registry)















