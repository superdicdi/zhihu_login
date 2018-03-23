import hmac
import json
import scrapy
import time

from hashlib import sha1


class ZhihuLoginSpider(scrapy.Spider):
    name = 'zhihu_login'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
               'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20'}

    def get_captcha(self, need_cap):
        """处理验证码 """
        if need_cap is False:
            return ""
        # with open('tudi_captcha.gif', 'wb') as fb:
        #     fb.write(data)
        return input('captcha:')

    def get_signature(self, grantType, clientId, source, timestamp):
        """处理签名"""
        hm = hmac.new(b'd1b964811afb40118a12068ff74a12f4', None, sha1)
        hm.update(str.encode(grantType))
        hm.update(str.encode(clientId))
        hm.update(str.encode(source))
        hm.update(str.encode(timestamp))
        return str(hm.hexdigest())

    def parse(self, response):
        print(response.body.decode("utf-8"))


    def start_requests(self):
        yield scrapy.Request('https://www.zhihu.com/api/v3/oauth/captcha?lang=cn',
                       headers=self.headers, callback=self.is_need_capture)

    def is_need_capture(self, response):
        yield scrapy.Request('https://www.zhihu.com/captcha.gif?r=%d&type=login' % (time.time() * 1000),
                             headers=self.headers, callback=self.capture, meta={"resp": response})

    def capture(self, response):
        with open('di_captcha.gif', 'wb') as f:
            # 下载图片必须以二进制来传输
            f.write(response.body)
            f.close()

        need_cap = json.loads(response.meta.get("resp", "").text)["show_captcha"] # {"show_captcha":false}表示不用验证码
        grantType = 'password'
        clientId = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
        source = 'com.zhihu.web'
        timestamp = str(int(round(time.time() * 1000)))  # 毫秒级时间戳 签名只按这个时间戳变化

        post_data = {
            "client_id": clientId,
            "username": "",  # 输入知乎用户名
            "password": "",  # 输入知乎密码
            "grant_type": grantType,
            "source": source,
            "timestamp": timestamp,
            "signature": self.get_signature(grantType, clientId, source, timestamp),  # 获取签名
            "lang": "cn",
            "ref_source": "homepage",
            "captcha": self.get_captcha(need_cap),  # 获取图片验证码
            "utm_source": ""
        }

        return [scrapy.FormRequest(
            url="https://www.zhihu.com/api/v3/oauth/sign_in",
            formdata=post_data,
            headers=self.headers,
            callback=self.check_login
        )]

    def check_login(self, response):
        # 验证是否登录成功
        print(response)
        yield scrapy.Request('https://www.zhihu.com/inbox', headers=self.headers)
        pass
