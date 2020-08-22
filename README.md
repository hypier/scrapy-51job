# 51job 爬虫

- 此爬虫采用scrapy框架，以redis作为地址缓存，以mongo作为内容存储
- 可以单独启用也可以导入[crawlab](https://github.com/crawlab-team/crawlab) 平台
- 项目启动后需要向redis中写入`51job:start_urls` list值

## 截图

### 1. 采集结果

![](https://oscimg.oschina.net/oscnet/up-b629086a42b70a9244c5f4ac04139dbd554.png)

![](https://oscimg.oschina.net/oscnet/up-6a181f18a1dcdfea43821a63b5e7c70e4db.png)

### 2. 爬虫管理平台

![](https://oscimg.oschina.net/oscnet/up-fbb17fb19ecfa3da0bbaa106457c183a463.png)

![](https://oscimg.oschina.net/oscnet/up-3a47dea57de50e5f62efb63ef0b378e23a4.png)

![](https://oscimg.oschina.net/oscnet/up-fca9e6a88c240d0875aa126e27a1359dbd3.png)

![](https://oscimg.oschina.net/oscnet/up-923e40a021d6600421d816e96e432d68ed0.png)