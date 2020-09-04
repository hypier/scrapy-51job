import json
import time
from urllib import parse

import requests
import scrapy

from scrapy_redis.spiders import RedisSpider

from company_resume_51job.customer_redis_dupe_filter import dupe_filter
from company_resume_51job.items import Job51Item


class ZhaopinSpider(RedisSpider):
    name = 'zhilian'  # 爬虫名
    allowed_domains = ['zhaopin.com']  # 允许访问的域名
    page_limit = 3
    city = 551
    salary_f = 15001
    salary_t = 25000
    kds = ['java', r'技术总监', r'架构师', r'java 技术经理']

    headers = {
        'authority': "fe-api.zhaopin.com",
        'pragma': "no-cache",
        'cache-control': "no-cache,no-cache",
        'accept': "application/json, text/plain, */*",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/83.0.4103.116 Safari/537.36",
        'content-type': "application/json;charset=UTF-8",
        'origin': "https://sou.zhaopin.com",
        'sec-fetch-site': "same-site",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': "https://sou.zhaopin.com/?p=2&jl=530&kw=java&kt=3",
        'accept-language': "zh-CN,zh;q=0.9,en;q=0.8",
    }

    def get_ref_url(self, kd, salary_f, salary_t, city):
        return 'https://sou.zhaopin.com/?jl={}&sf={}&st={}&kw={}&kt=3'.format(city, salary_f, salary_t, parse.quote(kd))

    def get_headers(self, ref_url):
        my_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/72.0.3626.119 Safari/537.36",
            "Referer": ref_url,
            "Content-Type": "application/x-www-form-urlencoded;charset = UTF-8"
        }
        return my_headers

    def start_requests(self):
        yield scrapy.Request(url="https://www.zhaopin.com", callback=self.parse, dont_filter=True)

    def parse(self, response, **kwargs):
        for kd in self.kds:
            for x in range(1, self.page_limit + 1):
                job_list = self.parse_page(kd, x)
                if not job_list:
                    continue

                for job in job_list:
                    yield job
        print('end')

    def parse_page(self, kd, page):
        payload = {
            'start': '{}'.format(90 * (page - 1)),
            'pageSize': '90',
            'cityId': '{}'.format(self.city),
            "salary": "{},{}".format(self.salary_f, self.salary_t),
            'workExperience': '-1',
            'companyType': '-1',
            'employmentType': '-1',
            'jobWelfareTag': '-1',
            'kw': kd,
            'kt': '3',
        }
        try:
            job_list = self.get_json(payload)
            print("第%s页正常采集 %s" % (page, parse.unquote(kd)))
            return job_list
        except Exception as msg:
            print("第%s页出现问题 %s , error: %s" % (page, parse.unquote(kd), msg))

    def get_url(self):
        resp = requests.get('http://139.9.119.18:8000/key=e4d1f73c78f19bb6c7db25f6b39dc5c6')
        resp_dict = json.loads(resp.text)
        x_zp_page_request_id = resp_dict['x_zp_page_request_id']
        x_zp_client_id = resp_dict['x_zp_client_id']
        MmEwMD = resp_dict['MmEwMD']
        url = f'https://fe-api.zhaopin.com/c/i/sou?x-zp-page-request-id={x_zp_page_request_id}' \
              f'&x-zp-client-id={x_zp_client_id}&MmEwMD={MmEwMD}'
        return url

    def get_json(self, payload):

        time.sleep(5)
        ses = requests.session()  # 获取session
        ref_url = self.get_ref_url(payload['kw'], self.salary_f, self.salary_t, self.city)
        ses.headers.update(self.get_headers(ref_url))  # 更新
        ses.get(ref_url)
        url = self.get_url()

        content = requests.post(url, json=payload, headers=self.headers)
        result = content.json()
        info = result['data']['results']
        info_list = []
        for job in info:
            job_url = job['positionURL']
            if dupe_filter(job_url, self.name, self.server):
                print('重复页：%s' % job_url)
                continue

            try:
                info = self.parse_job(job, ses)
                info_list.append(info)
            except Exception as msg:
                print("job 采集失败 %s -> %s" % (job_url, msg))

            # 将列表对象进行json格式的编码转换,其中indent参数设置缩进值为2
            # print(json.dumps(info_list, ensure_ascii=False, indent=2))
        # print(info_list)
        return info_list

    def parse_job(self, re, session):
        job = Job51Item()
        # job id
        job['id'] = re['number']
        # job website
        job['website'] = self.name
        # job time
        job['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # job url
        job['url'] = re['positionURL']

        # 职位名称
        job['name'] = re['jobName']
        # 公司名称
        job['co_name'] = re['company']['name']
        # 区域
        job['area'] = re['businessArea']
        # 工资
        job['salary'] = re['salary']
        job['exp'] = re['workingExp']['name']
        job['edu'] = re['eduLevel']['name']
        job['num'] = 1

        job['pub_time'] = re['updateDate'].split('-', 1)[1].split(' ')[0]
        job['otherq'] = re['updateDate']
        # 福利
        job['welfare'] = ','.join(re['welfare'])

        # 上班地址
        job['local'] = re['businessArea']

        # 公司类型
        job['co_type'] = re['company']['type']['name']
        # 公司行业
        job['co_trade'] = re['jobType']['items'][0]['name']
        job['co_url'] = re['company']['url']

        # time.sleep(1)
        # html_doc = session.get(job['url'])
        # soup = BeautifulSoup(html_doc.text, 'html.parser', from_encoding='utf-8')
        #
        # job_info = soup.find_all('div', class_='job-detail')
        # if job_info and len(job_info) > 0:
        #     # 职位信息
        #     job['info'] = job_info[0].get_text().strip()
        # else:
        #     print('没取到：' + job['url'])

        return job
