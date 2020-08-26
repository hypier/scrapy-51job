# -*- coding: utf-8 -*-

import logging

from proxyPool.ProxyPoolWorker import get_proxy_pool_worker

"""
    请求处理工具
@Author monkey
@Date 2017-12-16
"""


class ProxyMiddleware(object):
    # overwrite process request
    def process_request(self, request, spider):
        # Set the location of the proxy
        proxy_address = get_proxy_pool_worker().select_proxy_data()
        logging.debug("=====  ProxyMiddleware get a random_proxy:【 {} 】 =====".format(proxy_address))
        request.meta['proxy'] = proxy_address

    def process_exception(self, request, exception, spider):
        # print("exception  ============= ", exception)
        pass


""" 捕获异常中间层 """


class CatchExceptionMiddleware(object):
    def process_exception(self, request, exception, spider):
        try:
            proxy = request.meta['proxy']
            if 'http://' in proxy:
                proxy = proxy.replace('http://', '')
            else:
                proxy = proxy.replace('https://', '')

            get_proxy_pool_worker().plus_proxy_failed_time(proxy.split(':')[0])
        except Exception as e:
            logging.debug("===  访问页面: " + request.url + " 出现异常。\n %s", e)

    def process_responce(self, request, response, spider):
        if response.staus < 200 or response.staus >= 400:
            try:
                proxy = request.meta['proxy']
                if 'http://' in proxy:
                    proxy = proxy.replace('http://', '')
                else:
                    proxy = proxy.replace('https://', '')

                get_proxy_pool_worker().plus_proxy_failed_time(proxy.split(':')[0])
            except KeyError:
                logging.debug("===  无法正常访问到的页面: " + response.url + " ===")
        return response


""" 捕获重连中间层 """


class RetryMiddleware(object):
    def process_exception(self, request, exception, spider):
        try:
            proxy = request.meta['proxy']
            if 'http://' in proxy:
                proxy = proxy.replace('http://', '')
            else:
                proxy = proxy.replace('https://', '')

            get_proxy_pool_worker().plus_proxy_failed_time(proxy.split(':')[0])
            # print('ip  proxy  ===  ', proxy.split(':')[0])
        except Exception as e:
            logging.debug("===  访问页面: " + request.url + " 出现异常。\n %s", e)

    def process_responce(self, request, response, spider):
        if response.staus < 200 or response.staus >= 400:
            try:
                proxy = request.meta['proxy']
                if 'http://' in proxy:
                    proxy = proxy.replace('http://', '')
                else:
                    proxy = proxy.replace('https://', '')

                get_proxy_pool_worker().plus_proxy_failed_time(proxy.split(':')[0])
            except KeyError:
                logging.debug("===  无法正常访问到的页面: " + response.url + " ===")
        return response
