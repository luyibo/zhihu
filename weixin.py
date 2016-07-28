#coding=utf-8
__author__ = 'lyb'

import os
import re
import time
from PIL import Image
import requests
import xml.dom.minidom
import json
from bs4 import BeautifulSoup

class weixin():
    session = requests.session()
    headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 5.1; rv:33.0) Gecko/20100101 Firefox/33.0'
}
    uuid = ''
    DeviceID = "e940244352619129"

    def get_uuid(self):
        url = 'https://login.weixin.qq.com/jslogin'
        params = {
        'appid': 'wx782c26e4c19acffb',
        'fun': 'new',
        'lang': 'zh_CN',
        '_': int(time.time()),
    }
        response = self.session.get(url, params=params)
        data = response.content
        pattern = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
        res = re.search(pattern,data)
        code = res.group(1)
        self.uuid = res.group(2)
        if code=='200':
            return True
        return False

    def get_captcha(self):
        url = 'https://login.weixin.qq.com/qrcode/' + self.uuid
        parmas = {
            't':'webwx',
            '_':time.time()
        }
        response = self.session.get(url,headers=self.headers)
        with open('captcha.jpg','wb') as f:
            f.write(response.content)
            f.close()
        image = Image.open('captcha.jpg')
        image.show()
        image.close()

    def prelogin(self):
        self.tip = 1
        url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid=%s&tip=%s&_=%s' %\
              (self.tip, self.uuid, int(time.time()))
        response = self.session.get(url,headers=self.headers)
        data = response.content
        regx = r'window.code=(\d+);'
        res = re.search(regx,data)
        code = res.group(1)
        if code == '201':
            print u'成功扫描,请在手机上点击确认以登录'
            self.tip = 0
        elif code == '200':  # 已登录
            print u'正在登录...'
            regx = r'window.redirect_uri="(\S+?)";'
            pm = re.search(regx, data)
            self.redirect_uri = pm.group(1) + '&fun=new&version=v2&lang=zh_CN'
            self.base_uri = self.redirect_uri[:self.redirect_uri.rfind('/')]
        elif code == '408':  # 超时
            pass
        # elif code == '400' or code == '500':
        return code

    def login(self):
        response = self.session.get(self.redirect_uri)
        data = response.content
        soup = BeautifulSoup(data,'lxml')
        self.skey = soup.skey.string
        wxsid = soup.wxsid.string
        wxuin = soup.wxuin.string
        self.pass_ticket = soup.pass_ticket.string

        self.BaseRequest = {
            'DeviceID':self.DeviceID,
            'Sid':wxsid,
            'Skey':skey,
            'Uin':wxuin,
        }

        return True

    def webwxinit(self):
        url = self.base_uri + \
        '/webwxinit?pass_ticket=%s&skey=%s&r=%s' % (
            self.pass_ticket, self.skey, int(time.time()))
        params = {
            'BaseRequest':self.BaseRequest,
        }
        self.headers['ContentType'] = 'application/json; charset=UTF-8'
        response = self.session.post(url,data = json.dumps(params),headers=self.headers)
        data = response.content
        dic = json.loads(data)
        SyncKeylist = []
        for item in dic['SyncKey']['List']:
            SyncKeylist.append('%s_%s'%(item['Key'],item['Val']))
        SyncKey = '|'.join(SyncKeylist)
        ErrMsg = dic['BaseResponse']['ErrMsg']
        Ret = dic['BaseResponse']['Ret']

        if Ret==0:
            return True
        return False

    def webwxgetcontact(self):
        url = self.base_uri + \
        '/webwxgetcontact?pass_ticket=%s&skey=%s&r=%s' % (
            self.pass_ticket, self.skey, int(time.time()))

        response = self.session.get(url,headers=self.headers)
        data = response.content
        dic = json.loads(data)


