# coding: utf-8

# 音频文件自动下载脚本
# 音频文件抓取网址:http://m.sc.chinaz.com/yinxiao/HuanRaoYinXiao.html

import requests
from bs4 import BeautifulSoup
import json
import random
import time
import cookielib
from subprocess import call


import sys
reload(sys)
sys.setdefaultencoding('utf8')

s = requests.Session()

class VoiceDownload:

    def __init__(self):

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
            'Referer': 'http://m.sc.chinaz.com/'
        }









    # 获取列表页数据
    def get_page_html(self):
        try:
            url = "http://m.sc.chinaz.com/yinxiao/HuanRaoYinXiao.html"
            res = requests.get(url, headers=self.headers)
            html_str = res.text
            return html_str
        except Exception as e:
            print("获取使用列表页面:%s"% e)







if __name__ == '__main__':
    vd_test = VoiceDownload()
    result = vd_test.get_page_html()

    quit()