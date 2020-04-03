#!/usr/bin/env python3
import os, yaml
import time
import datetime
import socket  # 获取主机名
import psutil  # 获取CPU等信息
import logging
from argparse import ArgumentParser
from prometheus_client import Gauge, pushadd_to_gateway, CollectorRegistry


logging.basicConfig(
    filename='server.log',
    level=logging.WARNING,
    format='%(levelname)s:%(asctime)s:%(message)s'
)

class Server_info():

    def __init__(self):
        self.registry = CollectorRegistry()


    # 获取系统基本信息
    def baseinfo(self):
        hostname = socket.gethostname()
        user_conn = len(psutil.users())
        start_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        sys_runtime = os.popen('w').readline().split('users')[0].split('up')[1].strip()[:-1].strip()[:-1]
        process = os.popen('ps -ef |wc -l').read().split()[0]
        return {"hostname": hostname, "user_conn": user_conn, "sys_start_time": start_time, "now_time": now_time,
                "sys_runtime": sys_runtime, "process": process}


    # 获取CPU信息
    def cpuinfo(self):

        total_cpu = 0
        tmp = {}
        to_pre = lambda x: "{}%".format(str(round(x / total_cpu * 100, 2)))
        for i in range(len(psutil.cpu_times())):
            total_cpu += psutil.cpu_times()[i]

        for k, v in cpuinfo.items():
            tmp[k] = to_pre(eval(v))
        return tmp


    # 获取内存信息
    def meminfo(self):

        toStrGB = lambda x: "{}GB".format(str(round(psutil.virtual_memory().x / 1024 / 1024 / 1024)))
        tmp = {}

        for k, v in meminfo.items():

            tmp[k] = toStrGB(eval(v))

        return tmp


    def push2gateway(self):

        try:
            g_baseinfo = Gauge('baseinfo_test_metric', 'Description of gauge', ['hostname', 'now_time', 'sys_runtime'],
                               registry=self.registry)
            g_cpuinfo = Gauge('cpuinfo_test_metric', 'Description of gauge', ['user_use', 'cpu_pre', 'iowait'],
                              registry=self.registry)
            g_meminfo = Gauge('meminfo_test_metric', 'Description of gauge', ['total_mem', 'use_mem', 'mem_percent'],
                              registry=self.registry)

            baseinfo_dict = Server_ojb.baseinfo()
            cpuinfo_dict =Server_ojb.cpuinfo()
            meminfo_dict = Server_ojb.meminfo()


            g_baseinfo.labels(hostname=baseinfo_dict['hostname'], now_time=baseinfo_dict['now_time'],
                              sys_runtime=baseinfo_dict['sys_runtime'])
            g_cpuinfo.labels(user_use=cpuinfo_dict['user_use'], cpu_pre=cpuinfo_dict['cpu_pre'],
                             iowait=cpuinfo_dict['iowait'])
            g_meminfo.labels(total_mem=meminfo_dict['total_mem'], use_mem=meminfo_dict['use_mem'],
                             mem_percent=meminfo_dict['mem_percent'])


            pushadd_to_gateway(target, job='info_pushgateway', registry=self.registry)

        except Exception as e:
            logging.error(str(e))

if __name__ == '__main__':
    parser = ArgumentParser(description='describe')
    parser.add_argument("--verbose", help="Increase output verbosity",
                        action="store_const", const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('--filename', default='config.yaml')
    args = parser.parse_args()
    filename = os.path.join(os.path.dirname(__file__), args.filename).replace("\\", "/")
    f = open(filename)
    y = yaml.load(f, Loader=yaml.FullLoader)
    target = y['pushgateway']['targets']
    cpuinfo = y['cpuinfo']
    meminfo = y['meminfo']
    Server_ojb = Server_info()
    Server_ojb.push2gateway()











