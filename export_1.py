import psutil
import socket
from prometheus_client import Gauge,start_http_server
from time import sleep

g = Gauge('cup_use_percent_test_metric', 'Description of gauge',['hostip'])
host_ip = socket.gethostbyname(socket.getfqdn(socket.gethostname()))      #获取本机IP

def get_cup_use():
    cup_use_percent = psutil.cpu_percent(0.5)            #获取CPU使用率
    g.labels(hostip=host_ip).set(cup_use_percent)       #本机IP传入labels，CPU使用率传入value

if __name__ == '__main__':
    start_http_server(8006)           #8006端口启动
    while True:
        get_cup_use()
        print(111)
        sleep(10)
