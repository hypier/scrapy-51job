
def dupe_filter(url, name, server):
    from scrapy.utils import request
    from scrapy.http import Request

    key = "{}:{}".format(name, 'dupefilter')
    req = Request(url=url)
    result = request.request_fingerprint(req)
    added = server.sadd(key, result)

    return added == 0
