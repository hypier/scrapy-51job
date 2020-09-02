# -*- coding:utf-8 -*-
import requests
import json


resp = requests.get('http://139.9.119.18:8000/key=e4d1f73c78f19bb6c7db25f6b39dc5c6')
resp_dict = json.loads(resp.text)
print(resp_dict)

x_zp_page_request_id = resp_dict['x_zp_page_request_id']
x_zp_client_id = resp_dict['x_zp_client_id']
MmEwMD = resp_dict['MmEwMD']
url = f'https://fe-api.zhaopin.com/c/i/sou?x-zp-page-request-id={x_zp_page_request_id}&x-zp-client-id={x_zp_client_id}&MmEwMD={MmEwMD}'


headers = {
    'authority': "fe-api.zhaopin.com",
    'pragma': "no-cache",
    'cache-control': "no-cache,no-cache",
    'accept': "application/json, text/plain, */*",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    'content-type': "application/json;charset=UTF-8",
    'origin': "https://sou.zhaopin.com",
    'sec-fetch-site': "same-site",
    'sec-fetch-mode': "cors",
    'sec-fetch-dest': "empty",
    'referer': "https://sou.zhaopin.com/?p=2&jl=530&kw=python&kt=3",
    'accept-language': "zh-CN,zh;q=0.9,en;q=0.8",
    }

payload = {
    'start': '90',
    'pageSize': '90',
    'cityId': '530',
    'workExperience': '-1',
    'companyType': '-1',
    'employmentType': '-1',
    'jobWelfareTag': '-1',
    'kw': 'python',
    'kt': '3',
}

response = requests.post(url, json=payload, headers=headers)
print(response.text)