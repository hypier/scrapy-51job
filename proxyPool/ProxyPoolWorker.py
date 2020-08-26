# -*- coding: utf-8 -*-
import random

from proxyPool.dbManager.proxyDBManager import ProxyDBManager
from proxyPool.spiders.data5uSpider import Data5uSpider
from proxyPool.spiders.kuaidailiSpider import KuaidailiSpider
from proxyPool.spiders.xiciSpider import XiciSpider

from proxyPool.requester import requestEnginer

from apscheduler.schedulers.background import BackgroundScheduler
'''
    IP 代理池模块,主入口
@Author monkey
@Date 2017-12-17
'''


class ProxyPoolWorker(object):

    __MIN_PROXY_NUM = 15

    def __init__(self):

        self.__first = True
        # 连接数据库
        self.dbmanager = ProxyDBManager()
        # 创建数据库表
        self.dbmanager.drop_proxy_table()
        self.dbmanager.create_proxy_table()

    """ 
    把 ProxyPoolWorker 实现为单例 
    """
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '__instance'):
            new = super(ProxyPoolWorker, cls)
            cls.__instance = new.__new__(cls, *args)
        return cls.__instance

    """ 
    开始爬取 IP 代理 
    """
    def start_work(self):
        self.crawl_proxy_web()

        scheduler = BackgroundScheduler()  # 后台调度器
        # 后台每 10 秒执行一次
        # scheduler.add_job(self.__timedTask, 'interval', seconds=10)
        # 后台每 10 分钟执行一次
        scheduler.add_job(self.__check_ip_availability_task, 'interval', minutes=10)
        scheduler.start()

    """ 
    检查 IP 是否可用 
    """
    def __check_ip_availability_task(self):
        pass

    def crawl_proxy_web(self):

        spiders = [
            # XiciSpider,
            # Data5uSpider,
            KuaidailiSpider,
        ]

        # for spider in spiders:
        # 修改为随机抓取某个代理网站
        spider = random.choice(spiders)
        models = spider.get_proxies()
        filtered_models = requestEnginer.filter_unavailable_proxy(models)
        for each in filtered_models:
            self.dbmanager.insert_proxy_table(each)

    """
    随机获取一个 IP 代理地址
    """
    def select_proxy_data(self):
        proxy = self.dbmanager.select_random_proxy()
        if proxy is not '':
            proxy = self.dbmanager.select_random_proxy()
            return proxy

    """
    代理地址失效, 数据库连接失败次数 +1
    """
    def plus_proxy_failed_time(self, ip):
        self.dbmanager.plus_proxy_failed_time(ip)

    """
    停止爬取 IP 代理
    """
    def stop_work(self):
        self.dbmanager.close_connection()


proxy_pool = ProxyPoolWorker()
'''
获取 ProxyPoolWorker 实例对象
'''


def get_proxy_pool_worker():
    return proxy_pool
