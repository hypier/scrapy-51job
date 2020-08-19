# 51job 爬虫

- 此爬虫采用scrapy框架，以redis作为地址缓存，以mongo作为内容存储
- 可以单独启用也可以导入[crawlab](https://github.com/crawlab-team/crawlab) 平台
- 项目启动后需要向redis中写入`51job:start_urls` list值