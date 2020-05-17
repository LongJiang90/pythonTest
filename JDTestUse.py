# coding: utf-8

# 京东试用 自动申请脚本
# 试用网址:https://try.jd.com/activity/getActivityList?page=1

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

class JDTestUse:

    global cookieJar

    def __init__(self, u_name, u_password, minS, maxS, minP, keyW):
        self.userName = u_name
        self.uPassword = u_password
        self.minSecond = int(minS)
        self.maxSecond = int(maxS)
        self.minPrice = float(minP)
        self.keyWord = keyW

        self.page = 1
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
            'Referer': 'https://www.jd.com/'
        }
        self.allTestArr = [] # 当前页所有商品数组
        self.canApplyArr = [] # 根据条件筛选出的可以申请的商品数组
        self.enable = False


    def get_ten_page_of_once(self,count):
        # auth.jpg
        # 清空数组
        if len(self.allTestArr) != 0:
            del self.allTestArr[:]

        count_of_num = 5

        for index in range(count_of_num):
            page = count * 5 - (4-index)
            print("当前页数:%i" % (page))
            htmlStr = self.get_page_html(page)
            html_str = htmlStr.encode(encoding='utf-8')
            if not htmlStr:
                print("页面加载失败")
                return None

            besoup = BeautifulSoup(html_str, features='html.parser')
            div_str = besoup.find_all('div', attrs={'class': "con"})
            items = BeautifulSoup(str(div_str))
            uls = items.find_all('li')
            self.allTestArr.extend(uls)  # 2个数组拼接, append是加入元素

        print ("本次获取到的商品个数为:%i" % len(self.allTestArr))
        all_skuids = ""
        for index, child in enumerate(self.allTestArr):
            soup = BeautifulSoup(str(child))
            sp_activity_id = child.attrs['activity_id']
            sku_id = child.attrs['sku_id']  # 获取商品编号
            sp_name = soup.find('div', attrs={'class': "p-name"})

            #将所有商品ID拼接成,隔开的字符串
            if index == 0:
                all_skuids = sku_id
            else:
                all_skuids = all_skuids + "," + sku_id

        price_arr = self.goto_sp_prices(all_skuids)
        if isinstance(price_arr, type({'asd' : 'dsada'})):
            print("获取商品价格出错: %s   ---等待120s后重试" % price_arr)
            time.sleep(120)
            price_arr = self.goto_sp_prices(all_skuids)



        sp_ids = ""
        self.canApplyArr = []
        print("获取到了已加载的商品价格")
        for index, child in enumerate(self.allTestArr):
            price_obj = price_arr[index]
            price = float(price_obj['p'])
            # 判断价格是否高于设置的最低价格
            if price >= self.minPrice:
                # 判断名称关键词
                if self.have_key_word(sp_name.text) is False:
                    self.canApplyArr.append(child)
                    sp_activity_id = child.attrs['activity_id']
                    if index == 0:
                        sp_ids = sp_activity_id
                    else:
                        sp_ids = sp_ids + "," + sp_activity_id

        sp_ids = sp_ids[1:]
        print("所有符合条件的商品id为:%s" % sp_ids)

        appled_ids = self.appled_sp_ids(sp_ids)
        print("申请过的商品id为:%s" % appled_ids)

        for index, child in enumerate(self.canApplyArr):

            soup = BeautifulSoup(str(child))
            sp_activity_id = child.attrs['activity_id']
            # sku_id = child.attrs['sku_id'] # 获取商品编号
            sp_name = soup.find('div', attrs={'class': "p-name"})

            # 无法再列表页获取价格,获取出来都是:暂无报价,所以跳转到详情页获取
            # price = self.goto_sp_price(sku_id)

            # 判断是否已申请
            if (sp_activity_id not in appled_ids) or (appled_ids is ''):
                # 随机等待秒数
                sleep_s = random.randint(self.minSecond, self.maxSecond)
                print("申请中,等待%is" % sleep_s)
                # 进行申请
                time.sleep(sleep_s)
                apply_dic = self.apply_sp(sp_activity_id)
                if apply_dic is not None:
                    message = apply_dic['message']
                    if message is "请先登陆！":
                        # 在mac屏幕中弹出提示框
                        mes = "需要重新登录,当前页面:%i页,记得修改page后重新运行程序" % self.page
                        cmd = 'display notification \"' + \
                              mes + '\" with title \"京东试用脚本提示\"'
                        call(["osascript", "-e", cmd])

            else:
                print("\n" + sp_name.text.encode('gbk') + " - 已申请")

            if index == (len(self.canApplyArr)-1):
                time.sleep(10)
                self.page += 1
                self.get_ten_page_of_once(self.page)

    # 获取列表页数据
    def get_page_html(self, page):
        try:
            url = "https://try.jd.com/activity/getActivityList?page=" + str(page)
            res = requests.get(url, headers=self.headers)
            html_str = res.text
            return html_str
        except Exception as e:
            print("获取使用列表页面:%s"% e)

    # 过滤掉关键词,使用','分割
    def have_key_word(self, sp_title):
        if self.keyWord is '':
            return False
        keyArr = self.keyWord.split(',')
        have = False
        for key in keyArr:
            if key in sp_title:
                have = True
                return have

        return have
    # 传入商品id看是否已经申请了
    def appled_sp_ids(self, ac_ids):
        global cookieJar
        try:
            url = "https://try.jd.com/user/getApplyStateByActivityIds?activityIds=" + str(ac_ids)
            res = requests.post(url, headers=self.headers, cookies=cookieJar)
            jsStr = res.content
            jsonArr = json.loads(jsStr)
            appled_sp_ids = ''
            for dic in jsonArr:
                appled_sp_ids = appled_sp_ids + "," + str(dic['activityId'])

            # 每一个dic的数据{u'activityId': 313130, u'selected': 10}

            appled_sp_ids = appled_sp_ids[1:]
            return appled_sp_ids
        except Exception as e:
            print("获取已经申请过的id接口:%s"% e)

    # 传入商品ids,获取价格数组
    def goto_sp_prices(self, sku_ids):
        try:
            url = "https://p.3.cn/prices/mgets?skuIds=" + str(sku_ids) +"&origin=2"
            res = requests.get(url, headers=self.headers, cookies=cookieJar)
            jsStr = res.content
            jsonArr = json.loads(jsStr)
            return jsonArr
        except Exception as e:
            print("获取商品价格数组:%s"% e)

        # https://passport.jd.com/loginservice.aspx?callback=jQuery6123729&method=Login&_=1521011612072 点击申请时需要访问的请求,_=系统时间戳
        #申请链接:https://try.jd.com/migrate/apply?activityId=253891&source=0

    def apply_sp(self, sp_id):
        global cookieJar
        try:
            url = "https://try.jd.com/migrate/apply?activityId=" + str(sp_id) + "&source=0"
            res = requests.post(url, headers=self.headers, cookies=cookieJar)
            html_str = res.text
            print(html_str)
            dic = json.loads(str(html_str))
            return dic
        except Exception as e:
            print("申请试用页面:%s"% e)




    def get_login_data(self):
        url = 'https://passport.jd.com/new/login.aspx'
        html = s.get(url, headers=self.headers).content
        soup = BeautifulSoup(html, 'html.parser')
        display = soup.select('#o-authcode')[0].get('style')
        auth_code = ''
        if not display:
            print('需要验证码。。。')
            auth_code_url = soup.select('#JD_Verification1')[0].get('src2')
            auth_code = self.get_auth_img(auth_code_url)
        uuid = soup.select('#uuid')[0].get('value')
        eid = soup.select('#eid')[0].get('value')
        fp = soup.select('input[name="fp"]')[0].get('value')  # session id
        _t = soup.select('input[name="_t"]')[0].get('value')  # token
        login_type = soup.select('input[name="loginType"]')[0].get('value')
        pub_key = soup.select('input[name="pubKey"]')[0].get('value')
        sa_token = soup.select('input[name="sa_token"]')[0].get('value')

        data = {
            'uuid': uuid,
            'eid': eid,
            'fp': fp,
            '_t': _t,
            'loginType': login_type,
            'loginname': self.userName,
            'nloginpwd': self.uPassword,
            'chkRememberMe': True,
            'authcode': '',
            'pubKey': pub_key,
            'sa_token': sa_token,
            'authCode': auth_code
        }
        return data

    def get_auth_img(self, url):
        auth_code_url = 'http:' + url
        auth_img = s.get(auth_code_url, headers=self.headers)
        with open(sys.path[0] + '/auth.jpg', 'wb') as f:
            f.write(auth_img.content)
        code = input('请输入验证码(例:\'xxxx\')：')
        return code

    def login(self):
        """
        登录
        :return:
        """
        url = 'https://passport.jd.com/uc/loginService'
        data = self.get_login_data()
        headers = {
            'Referer': 'https://passport.jd.com/uc/login?ltype=logout',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
            'X-Requested-With': 'XMLHttpRequest'
        }
        global cookieJar
        # 初始化一个CookieJar来处理Cookie
        cookieJar = cookielib.CookieJar()
        login_re = s.post(url, data=data, headers=headers)
        cookieJar = login_re.cookies


        content = login_re.text

        # # 初始化一个CookieJar来处理Cookie
        # cookieJar=cookielib.CookieJar()
        # # 实例化一个全局opener
        # opener= s.build_opener(requests.HTTPCookieProcessor(cookieJar))
        # # 获取cookie
        # req=requests.Request(auth_url,post_data,headers)
        # result = opener.open(req)
        # # 访问主页 自动带着cookie信息
        # # result = opener.open(‘http://i.jd.com/user/info‘)

        result = json.loads(content[1: -1])
        return result










if __name__ == '__main__':
    # 从JD_Configer.json文件中读取配置
    jd_configer = open("JD_Configer.json")
    setting = json.load(jd_configer, encoding="utf-8")
    user_name = setting["name"]
    user_password = setting["password"]
    minS = setting["minTime"]
    maxS = setting["maxTime"]
    minP = setting["minPrice"]
    keyW = setting["keyWord"]

    jd_test = JDTestUse(user_name, user_password, minS, maxS, minP, keyW)
    result = jd_test.login()

    jd_test.get_ten_page_of_once(jd_test.page)

    quit()