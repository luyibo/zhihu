#coding=utf-8
__author__ = 'lyb-mac'
import sys
reload(sys)

sys.setdefaultencoding('utf8')
import requests
import re
import json
from bs4 import BeautifulSoup as bs
from PIL import Image

class zhihu():
    def __init__(self):
        self.data = {
            'email':'1428260548@qq.com',
            'password':'luyibo',
            'remember_me':'true',
        }
        self.s = requests.session()
        self.header = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/601.6.17 (KHTML, like Gecko) Version/9.1.1 Safari/601.6.17',
                       'Referer':'https://www.zhihu.com/',}
        self.url1 = 'http://www.zhihu.com'
        self.url2 = 'https://www.zhihu.com/captcha.gif?r=1467249038299&type=login'
        self.url3 = 'https://www.zhihu.com/login/email'
        self.url4 = 'http://www.zhihu.com'
        self.url5 = 'https://www.zhihu.com/node/HomeFeedListV2'

    def get_xsrf(self):
        self.url1 = 'http://www.zhihu.com'
        self.xsrf = bs(self.s.get(self.url1,headers=self.header).content,'lxml').find(type='hidden')['value']
        return self.xsrf

    def get_captcha(self):
        self.url2 = 'https://www.zhihu.com/captcha.gif?r=1467249038299&type=login'
        captcha = self.s.get(self.url2,headers=self.header)
        with open('captcha.gif','w') as f:
            f.write(captcha.content)
            f.close()

    def login(self):

        self.url3 = 'https://www.zhihu.com/login/email'
        self.data['_xsrf'] = self.get_xsrf()
        self.get_captcha()
        im = Image.open('captcha.gif')
        im.show()
        im.close()
        self.captcha = raw_input('请输入验证码: ')
        self.data['captcha'] = self.captcha
        r = self.s.post(self.url3,headers=self.header,data=self.data)
        if r.status_code==200:
            print '登陆成功'
        else:
            print '失败'
        self.cookies = r.cookies
        r = self.s.get(self.url4,headers=self.header,cookies=self.cookies).content


    def get_html(self,url):
        r = self.s.get(url,headers=self.header,cookies=self.cookies).content
        ALL = bs(r,'lxml').find_all('div',class_='feed-item')
        self.start = ALL[-1].get('id')
        with open('zhihu1.txt','w+') as f:
            for each in ALL:
                f.write(each.find('h2').string)
                f.write('------------------')
                '''a = each.find('textarea')
                if a:
                    a = re.sub('<br>','\n',a.text)
                    a = re.sub('<p>|</p>','\t',a)
                    a = re.sub('<b>|</b>','',a)
                    a = re.sub('<li>|</li>','\t',a)
                    a = re.sub('<a .*?>|</a>','',a)
                    a =re.sub('<blockquote>|</blockquote>','',a)
                    a = re.sub('<u>|</u>','',a)
                    a = re.sub('<i .*?>|</i>','',a)
                    a = re.sub('<ul>|</ul>','',a)
                    f.write( a)
                else:
                     f.write( 'None')

                if each.find('div',class_='zm-item-answer-author-info'):
                     f.write( each.find('div',class_='zm-item-answer-author-info').a.string)
                else:
                     f.write( 'None')
                if each.find('a',class_='zm-item-vote-count'):
                     f.write( each.find('a',class_='zm-item-vote-count').string)
                else:
                     f.write ('None')'''

    def get_next(self,url):
        dic = {}


        for x in range(20,80,20):
            dic["offset"] = x
            dic["start"] = self.start[5:]
            formdata = {'method':'next','_xsrf':self.xsrf}
            p = json.dumps(dic)
            formdata["params"] = p
            t = self.s.post(url,headers=self.header,data=formdata)
            for e in json.loads(t.text)['msg']:
                print bs(e,'lxml').find('h2').string
                self.start = bs(e,'lxml').find('div',class_='feed-item').get('id')



    def main(self):
        self.login()
        self.get_html(self.url4)
        self.get_next(self.url5)


zhihu = zhihu()
zhihu.main()