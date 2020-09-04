import time
from urllib import parse
import requests
import scrapy
from bs4 import BeautifulSoup
from scrapy_redis.spiders import RedisSpider

from company_resume_51job.customer_redis_dupe_filter import dupe_filter
from company_resume_51job.items import Job51Item


class JobSpider(RedisSpider):
    name = 'lagou'
    allowed_domains = ['lagou.com']

    page_limit = 3
    city = parse.quote('重庆')
    salary = '15k-25k'
    kds = ['java', r'技术总监', r'架构师', r'java 技术经理']

    def get_ref_url(self, kd, salary, city):
        return 'https://www.lagou.com/jobs/list_{}?px=new&yx={}&city={}#order&cl=false&fromSearch=true' \
               '&labelWords=&suginput='.format(parse.quote(kd), salary, city)

    def get_headers(self, ref_url):
        my_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/72.0.3626.119 Safari/537.36",
            "Referer": ref_url,
            "Content-Type": "application/x-www-form-urlencoded;charset = UTF-8"
        }
        return my_headers

    def start_requests(self):
        yield scrapy.Request(url="https://www.lagou.com", callback=self.parse, dont_filter=True)

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

        url = 'https://www.lagou.com/jobs/positionAjax.json?px=new&yx={}&city={}&needAddtionalResult=false' \
            .format(self.salary, self.city)
        data = {
            'first': 'false',
            'pn': page,
            'kd': kd,
            'sid': ''
        }
        try:
            job_list = self.get_json(url, data)
            print("第%s页正常采集 %s" % (page, parse.unquote(kd)))
            return job_list
        except Exception as msg:
            print("第%s页出现问题 %s , error: %s" % (page, parse.unquote(kd), msg))

    def get_json(self, url, data):

        time.sleep(5)
        ses = requests.session()  # 获取session
        ref_url = self.get_ref_url(data['kd'], self.salary, self.city)
        ses.headers.update(self.get_headers(ref_url))  # 更新
        ses.get(ref_url)
        content = ses.post(url=url, data=data)
        result = content.json()
        info = result['content']['positionResult']['result']
        show_id = result['content']['showId']
        info_list = []
        for job in info:
            job_url = 'https://www.lagou.com/jobs/{}.html'.format(job["positionId"])
            if dupe_filter(job_url, self.name, self.server):
                print('重复页：%s' % job_url)
                continue

            try:
                info = self.parse_job(job, ses, show_id)
                info_list.append(info)
            except Exception as msg:
                print("job 采集失败 %s -> %s" % (job_url, msg))

            # 将列表对象进行json格式的编码转换,其中indent参数设置缩进值为2
            # print(json.dumps(info_list, ensure_ascii=False, indent=2))
        # print(info_list)
        return info_list

    def parse_job(self, re, session, show_id):
        job = Job51Item()
        # job id
        job['id'] = re["positionId"]
        # job website
        job['website'] = self.name
        # job time
        job['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # job url
        job['url'] = 'https://www.lagou.com/jobs/{}.html?show={}'.format(re["positionId"], show_id)

        # 职位名称
        job['name'] = re["positionName"]
        # 公司名称
        job['co_name'] = re['companyFullName']
        # 区域
        job['area'] = re['district']
        # 工资
        job['salary'] = re['salary']
        job['exp'] = re['workYear']
        job['edu'] = re['education']
        job['num'] = 1

        job['pub_time'] = re['createTime'].split('-', 1)[1].split(' ')[0]
        job['otherq'] = re['formatCreateTime']
        # 福利
        job['welfare'] = re['positionAdvantage']

        # 上班地址
        if re['businessZones'] is not None and len(re['businessZones']) > 0:
            job['local'] = ' '.join(re['businessZones'])

        # 公司类型
        job['co_type'] = re['financeStage']
        # 公司行业
        job['co_trade'] = re['industryField']

        time.sleep(1)
        html_doc = session.get(job['url'])
        soup = BeautifulSoup(html_doc.text, 'html.parser', from_encoding='utf-8')

        job_info = soup.find_all('div', class_='job-detail')
        if job_info and len(job_info) > 0:
            # 职位信息
            job['info'] = job_info[0].get_text().strip()
        else:
            print('没取到：' + job['url'])

        job_local = soup.find('div', class_='work_addr')
        if job_local and len(job_local) > 0:
            job['local'] = job_local.text.replace(' ', '').replace('\n', '').replace('查看地图', '')

        job_home = soup.find_all('i', class_='icon-glyph-home')
        if job_home and len(job_home) > 0:
            # 公司网址
            href = job_home[0].parent.find('a')
            if href:
                job['co_url'] = href.attrs['href']

        return job
