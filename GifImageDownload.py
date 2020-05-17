# coding: utf-8

# Gif图片自动下载脚本 并自动使用OpenCV去除水印
# 图片文件抓取网址:https://m.kengdie.com/category/dongtaitu/
from imp import reload

import requests
import re
import json
import random
import time
import datetime
from subprocess import call
import http.cookiejar

import cv2
import numpy as np
import imageio
from PIL import Image
import glob

import sys
import os

from PIL import Image, ImageFont, ImageDraw, ImageSequence

reload(sys)

s = requests.Session()

class GifImageDownload:

    def __init__(self):

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
            'Referer': 'http://m.sc.chinaz.com/'
        }
        self.base_path = sys.path[0] + '/TodayGif/'  # 获取当前路径
        today = datetime.date.today()

        self.todayStr = str(today.year) + str(today.month) + str(today.day)



    def get_today_gif(self, page):

        html_str = self.get_page_html(page)


        if html_str == None:
            print('获取到的网页字符串为空，请检查重试')
            return

        #正则表达式 找到图片网址数组
        imgs_url_arr = re.findall("http://(.*?).jpg", html_str.decode('utf-8'))

        for idx, img_url in enumerate(imgs_url_arr):

            need_download = False

            # 获取出来的是静态图片，需要将url中 thumb150 替换为 large 有部分是将 large替换为 thumb150
            if img_url.find('thumb150') != -1:
                img_url = img_url.replace('thumb150', 'large')
                need_download = True

            # if img_url.find('large') != -1:
            #     img_url = img_url.replace('large', 'thumb150')
            #     need_download = true

            if need_download == True:
                img_url = 'http://' + img_url + '.jpg'
                self.download_and_save_one_gif(img_url, idx)
            else:
                print('当前网址没有对应的文件夹名称，无效网址，不下载，网址：%s index：%s' % img_url, str(idx))



    # 获取列表页数据  page由1开始
    def get_page_html(self, page):
        try:
            if page == 1:
                url = "https://m.kengdie.com/category/dongtaitu/"
            else:
                url = "https://m.kengdie.com/category/dongtaitu/" + 'page/' + str(page) + '/'

            res = requests.get(url, headers=self.headers)
            htmlStr = res.text.encode(encoding='utf-8')
            # encode_type = chardet.detect(htmlStr)
            # htmlStr = htmlStr.decode(encode_type['encoding'])
            # html_str = htmlStr.encode(encoding='utf-8')
            return htmlStr
        except Exception as e:
            print("获取使用列表页面:%s" % e)


    def download_and_save_one_gif(self,imgUrl,idx):
        name = self.todayStr + '_' + str(idx)
        path = self.base_path + name + '.gif'

        # 判断是否已经存在相同图片，有就直接去获取了来删除水印
        had = os.path.exists(path)
        if had == True:
            # self.deleteWaterYin(path)
            return

        # 下载图片
        headers = {
        # 'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        # 'Connection': 'keep-alive',
        'Referer': 'http://ww3.sinaimg.cn/',
        # 'Host': 'i.meizitu.net',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
        }
        img = requests.get(imgUrl, headers=headers).content
        # 保存图片
        with open(path, 'wb') as f:
            f.write(img)

        self.deleteWaterYin(path)






    # 删除水印
    def deleteWaterYin(self, gifPath):
        imgList = imageio.mimread(gifPath)
        newList = []
        for subImg in imgList:
            new = np.clip(2.0 * subImg - 160, 0, 255).astype(np.uint8)

            # dimg = self.compress_image(new)

            newList.append(new)

        imageio.mimsave(gifPath, newList, 'GIF', duration=1)


    # 根据图片list创建Gif图片
    def creat_gif(self, image_list, gif_name, duration=2):
        """
        生成gif文件，原始图像仅仅支持png格式；
        gif_name : 字符串，所生成的gif文件名，带.gif文件名后缀；
        path : 输入图像的路径；
        duration : gif图像时间间隔，这里默认设置为1s,当然你喜欢可以设置其他；
        """
        # 创建一个空列表，用来存源图像
        frames = []

        # 利用方法append把图片挨个存进列表

        for image_name in image_list:
            frames.append(imageio.imread(image_name))

        # 保存为gif格式的图


        return

    # 压缩大小，最大1.5M
    def compress_image(self, sImg):
        # print(filename)
        # 打开原图片压缩
        w, h = sImg.size
        print(w, h)
        # dImg = sImg.resize((w * 0.5, 1080 * 0.5), Image.ANTIALIAS)  # 设置压缩尺寸和选项，注意尺寸要用括号
        # # 小米6: 1008 * 754
        # # 320*240  640*480 800*600 1024*768 1152*864 1280*960 1400*1050 1600*1200 2048*1536
        # # 如果不存在目的目录则创建一个
        # comdic = "%scompress/" % self.base_path
        # if not os.path.exists(comdic):
        #     os.makedirs(comdic)
        #
        # # 压缩图片路径名称
        # f1 = imgPath.split('/')
        # f1 = f1[-1].split('\\')
        # f2 = f1[-1].split('.')
        # f2 = '%s%s1%s' % (comdic, f2[0], imgPath)
        # # print(f2)
        # dImg.save(f2)  # save这个函数后面可以加压缩编码选项JPEG之类的
        # print("%s compressed succeeded" % f1[-1])


    # 给Gif加水印
    def watermark_on_gif(in_gif, out_gif, text='scratch8'):

        """本函数给gif动图加水印"""

        frames = []

        myfont = ImageFont.truetype("msyh.ttf", 12)  # 加载字体对象

        im = Image.open(in_gif)  # 打开gif图形

        water_im = Image.new("RGBA", im.size)  # 新建RGBA模式的水印图

        draw = ImageDraw.Draw(water_im)  # 新建绘画层

        draw.text((10, 10), text, font=myfont, fill='red')

        for frame in ImageSequence.Iterator(im):  # 迭代每一帧
            frame = frame.convert("RGBA")  # 转换成RGBA模式
            frame.paste(water_im, None)  # 把水印粘贴到frame
            frames.append(frame)  # 加到列表中

            newgif = frames[0]  # 第一帧

        # quality参数为质量，duration为每幅图像播放的毫秒时间

        newgif.save(out_gif, save_all=True,
                    append_images=frames[1:], quality=85, duration=100)
        im.close()



if __name__ == '__main__':
    gi_test = GifImageDownload()
    gi_test.get_today_gif(2)

    # src = cv2.imread(gi_test.base_path + '2020513_10.gif')
    # gi_test.deleteWaterYin(src)

    quit()
