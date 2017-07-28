#-*- coding:utf8 -*-
__author__ = 'Administrator'
import re
from bs4 import BeautifulSoup
import os
import time
import random
import requests
import lxml
import urllib
import urllib2
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


se = requests.session()

class Pixiv():

    def __init__(self):
        self.base_url = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
        self.login_url = 'https://accounts.pixiv.net/api/login?lang=zh'
        self.target_url = 'https://www.pixiv.net/bookmark.php'
        self.main_url = 'http://www.pixiv.net'
        # headers只要这两个就可以了,之前加了太多其他的反而爬不上
        self.headers = {
            'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }
        self.pixiv_id = ''
        self.password = ''
        self.post_key = []
        self.return_to = 'https://www.pixiv.net/bookmark.php'
        self.load_path = 'F:\Pixiv_pic\\'
        self.ip_list = [
            # '1.194.162.78	808',
            # '1.194.162.147	808',
            # '123.55.159.45  808',
            # '171.12.178.189	 808',
            # '123.163.163.211	808',
            # '1.192.245.235	8118	',
            # '171.15.90.18	808',
            # '171.13.13.175	808'
            # '123.55.190.1	11129'
            # '171.13.3.71	808'
        ]    #本来打算使用代理的   后来还是算了
        self.defeatFileList = []
        self.url_id = ''
        self.picNums = 0

    def login(self):
        post_key_html = se.get(self.base_url, headers=self.headers).text
        # print post_key_html  #登陆页的HTML
        post_key_soup = BeautifulSoup(post_key_html, 'lxml')
        self.post_key = post_key_soup.find('input')['value']
        # print self.post_key    #获取到的post_key
        # 上面是去捕获postkey
        data = {
            'pixiv_id': self.pixiv_id,
            'password': self.password,
            'return_to': self.return_to,
            'post_key': self.post_key
        }
        response = se.post(self.login_url, data=data, headers=self.headers)  #向服务器post这些信息，服务器会返回一个response对象，再调用response对象的方法来查看状态码和编码
        # print response.status_code
        # print response.content.decode()
        f = se.get(self.return_to,headers = self.headers)  #向服务器请求这个页面，得到这个页面的信息，调用.text()方法 打印出HTML的信息
        # print f.status_code
        # print f.text
        bookmarkHtml = f.text
        self.getBookmarkPageValues(bookmarkHtml)
        # self.getBookmarkHtml_Meber_listurl(bookmarkHtml)  #将收藏页的HTML传递给getBookmarkHtml方法

    def getBookmarkPageValues(self,bookmarkpageHtml,timeout = 5,proxy = None,num_entries = 5):

                    #没学会使用代理   就先放在这了  不过这个爬虫被反爬的概率没有那么高  暂时就不用了
        '''
        if proxy is None:
            try:
                return se.get(bookmarkpageHtml, headers=self.headers, timeout=timeout)
            except:
                if num_entries > 0:
                    print '获取网页出错,5秒后将会重新获取倒数第', num_entries, '次'
                    time.sleep(5)
                    return self.getBookmarkPageValues(bookmarkpageHtml, timeout, num_entries = num_entries - 1)
                else:
                    print '开始使用代理'
                    time.sleep(5)
                    ip = ''.join(str(random.choice(self.ip_list))).strip()
                    now_proxy = {'http': ip}
                    return self.getBookmarkPageValues(bookmarkpageHtml, timeout, proxy = now_proxy)
        else:
            try:
                return se.get(bookmarkpageHtml, headers=self.headers, proxies=proxy, timeout=timeout)
            except:
                if num_entries > 0:
                    print '正在更换代理,5秒后将会重新获取第', num_entries, '次'
                    time.sleep(5)
                    ip = ''.join(str(random.choice(self.ip_list))).strip()
                    now_proxy = {'http': ip}
                    return self.getBookmarkPageValues(bookmarkpageHtml, timeout, proxy = now_proxy, num_entries = num_entries - 1)
                else:
                    print '使用代理失败,取消使用代理'
                    return self.getBookmarkPageValues(bookmarkpageHtml, timeout)
        '''

        #写一个能检测收藏夹页面共有多少页收藏的方法，将返回值再传递给getBookmarkHtml_Meber_listurl()
        bookmark_soup = BeautifulSoup(bookmarkpageHtml,'lxml')
        allpage = bookmark_soup.find('ul',class_='page-list').get_text()
        pagevalues = str(allpage[-1:])
        now_page = bookmark_soup.find('li',class_='current').get_text()
        now_page = str(now_page)
        print '您的收藏夹共有%s页 当前位于第%s页' % (pagevalues,now_page)
        x = int(now_page)
        pagenum = int(pagevalues)
        for x in range(1,pagenum+1):
            if x == 1:
                url = 'https://www.pixiv.net/bookmark.php'
                bookmarkHtml = se.get(url,headers=self.headers).text
                self.getBookmarkHtml_Meber_listurl(bookmarkHtml)
            else:
                url = 'https://www.pixiv.net/bookmark.php?rest=show&order=desc&p=%d' % x
                bookmarkHtml = se.get(url,headers=self.headers).text
                self.getBookmarkHtml_Meber_listurl(bookmarkHtml)
            x +1

    def getBookmarkHtml_Meber_listurl(self,html):
        r = r'a href=".+?\.php\?.+?_id=(\d+?)" class'
        p_member_illust_ = re.compile(r)
        A_member_illust_url = re.findall(p_member_illust_,html)
        # print A_member_illust_url
        B_member_illust_url = list(set(A_member_illust_url))   #将得到的收藏链接中重复的链接id值去掉  免得重复执行

        C_member_illust_urlList = []

        x = 0
        print '本收藏页所有收藏链接为：'
        for illust_url in B_member_illust_url:
            global li_url
            li_url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=%s' % illust_url   #根据收藏链接的id值和收藏链接的格式，生成收藏链接
            C_member_illust_urlList.append(li_url)
            print li_url
            x+=1
        print '本页共%s个收藏' % x

        for i in range(0,x):
            c = i+1
            print '正在获取本页第%s个收藏的页面' % c
            try:
                li_html = se.get(C_member_illust_urlList[i],headers = self.headers).text    #打印出这个收藏链接的HTML   其中包含收藏链接页的图片
            except:
                self.defeatFileList.append(C_member_illust_urlList[i])
                print '页面获取失败  可能触发了反爬虫 url已添加进失败列表 歇会再试吧'
            print C_member_illust_urlList[i]
            self.url_id = C_member_illust_urlList[i][-8:]
            # print li_html
            self.get_li_html_url(li_html)   #将收藏链接页的HTML传递给这个方法，来解析其中的图片链接
            time.sleep(random.randint(1,5))

    def get_li_html_url(self,li_html):
        li_soup = BeautifulSoup(li_html,'lxml')  #获取这个图片页面的html对象

        readMorelink = li_soup.find_all('a',class_ ='read-more js-click-trackable')
        # moreImg_value = str(readMorelink.get_text())[4:-1]
        if readMorelink == []:   #如果查看更多的值为空，
            for imgLink in li_soup.find_all('img',class_='original-image'):   #找到原图的链接
                rawimg_title = imgLink.get('alt')                             #分析出原图的标题
                rawimg_url = imgLink.get('data-src')                          #分析出原图的URL
                rawimg_h = imgLink.get('height')                              #分析出原图的高
                rawimg_w = imgLink.get('width')                               #分析出原图的宽
                str_urlTOimgType = str(rawimg_url)                            #将原图链接str化来分析原图的格式是jpg 还是png
                rawimg_type = str_urlTOimgType[-3:]
                if rawimg_type == 'jpg':
                                            #这两句输出  在打包EXE的时候老是出故障  干脆注释掉了
                    print '%s 图片标题：%s 尺寸：%s x %s  %s' % (rawimg_url,rawimg_title,rawimg_h,rawimg_w,rawimg_type)
                else:
                    rawimg_type = 'png'
                    print '%s 图片标题：%s 尺寸：%s x %s  %s' % (rawimg_url,rawimg_title,rawimg_h,rawimg_w,rawimg_type)
                self.download_image(rawimg_url,rawimg_title,rawimg_type)   #将分析出来的数据传递到download_image方法进行图片的保存操作
                time.sleep(random.randint(1,5))
        else:
            print '此页面有多张图片，将使用其他方法进行解析'
            self.morePics_deal(readMorelink)

            #如果查看更多的值不为空的话，暂时还没有想好怎么写 可以写一个方法来专门处理单个收藏夹有多张图片的方法

    def download_image(self,img_url,rawimg_title,rawimg_type):
        src_headers = self.headers
        src_headers['Referer'] = li_url
        try:
            img = se.get(img_url,headers = src_headers)    #获取原图页面
            bytes = img.content    #获取原图数据
        except:
            print '图片获取失败 可能触发了反爬虫 请稍后重新运行'

        f_name = rawimg_title.replace('?', '_').replace('/', '_').replace('\\', '_').replace('*', '_').replace('|', '_').replace('>', '_').replace('<', '_').replace(':', '_').replace('"', '_').strip()
        try:
            is_exists = os.path.exists(self.load_path+f_name+'.'+rawimg_type)
            if is_exists == True:
                print '图片名称重复，图片 %s 准备更名后保存'% f_name
                newf_name = self.picNameRepeat(f_name)
                f = open('F:\Pixiv_pic\\'+newf_name+'.'+rawimg_type,'wb')        #将图片以二进制形式进行保存
                f.write(bytes)      #将文件写入打开的目录
                f.flush()         #将数据更新至打开的目录
                f.close()         #关闭目录
                print '图片 %s 已保存成功' % newf_name
            else:
                f = open(self.load_path+f_name+'.'+rawimg_type,'wb')        #将图片以二进制形式进行保存
                f.write(bytes)      #将文件写入打开的目录
                f.flush()         #将数据更新至打开的目录
                f.close()         #关闭目录
                print '图片 %s 已保存成功'% f_name
        except:
            print '图片 %s 保存失败,图片链接已保存在失败列表中' % f_name
            self.defeatFileList.append(img_url)

    def picNameRepeat(self,f_name):
        x = random.randint(1,100)
        f_name1 = str(f_name)
        nums = str(x)
        f_name2 = f_name1+nums
        return f_name2

    def morePics_deal(self,readMorelink):
        text = str(readMorelink)
        text2 = text[226:-5]
        text3 = text2.decode('unicode-escape')
        text4 = text3[5:-2]
        # print text4
        # print self.url_id
        to_url = 'https://www.pixiv.net/member_illust.php?mode=manga&illust_id=%s' % self.url_id
        try:
            html_1 = se.get(to_url,headers = self.headers).text
        except:
            print '可能被触发了反爬虫  歇会吧'
        html_soup = BeautifulSoup(html_1,'lxml')
        imglist = html_soup.find_all('a',class_ = 'full-size-container _ui-tooltip')
        for img in imglist:
            img_url = img.get('href')
            s = str(img_url)
            # print s
            to_img_url = 'https://www.pixiv.net%s' % s
            # print to_img_url
            self.picNums+=1
            self.morePics_download(to_img_url)

    def morePics_download(self,to_img_url):
        print to_img_url
        html_2 = se.get(to_img_url,headers = self.headers).text
        html_2_soup = BeautifulSoup(html_2,'lxml')
        picTitle = str(html_2_soup.find('title'))
        r_title = picTitle[7:-15]
        title = r_title.replace('?', '_').replace('/', '_').replace('\\', '_').replace('*', '_').replace('|', '_').replace('>', '_').replace('<', '_').replace(':', '_').replace('"', '_').strip()
        img = html_2_soup.find('img')
        imgSrc = img.get('src')
        imgType = str(imgSrc)[-3:]
        print '%s图片标题 %s %s' % (imgSrc,title,imgType)
        self.makeDirWithMorePics(imgSrc,imgType)

    def makeDirWithMorePics(self,imgSrc,imgType):
        new_load_path = self.load_path+'id'+self.url_id
        is_exists = os.path.exists(new_load_path)
        if is_exists == False:
            print '创建新的文件夹 id%s'% self.url_id
            os.makedirs(new_load_path)
        picNo = str(imgSrc)[66:-4]
        # print picNo
        try:
            img = se.get(imgSrc,headers = self.headers)    #获取原图页面
            bytes = img.content    #获取原图数据
        except:
            print '图片获取失败 可能触发了反爬虫 失败的图片链接已添加进失败列表 请稍后重新运行'
        f_name = picNo
        f = open(new_load_path+'\\'+f_name+'.'+imgType,'wb')        #将图片以二进制形式进行保存
        f.write(bytes)      #将文件写入打开的目录
        f.flush()         #将数据更新至打开的目录
        f.close()         #关闭目录
        print '图片 %s 已保存成功' % f_name

    def work(self):
        f = open(self.load_path+'user_info.ini','r')
        lines = f.readlines()
        f.close()
        self.pixiv_id = lines[0][8:-1]
        self.password = lines[1][10:]

        self.login()
        print '保存失败的图片URL'
        for defeatUrl in self.defeatFileList:
            f2 = open(self.load_path+'defeatFileList.txt','a')
            f2.write(defeatUrl+'\n')
            f2.close()
            print defeatUrl

pixiv = Pixiv()
pixiv.work()
