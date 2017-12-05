# -*- coding: utf-8 -*-
__author__ = 'ogaki'

# import urllib.error, urllib.parse
import urllib
import requests
from bs4 import BeautifulSoup
import mechanize
import re
# import html.entities
import time
import unicodedata
import itertools
import os
import pickle

class Config:
    MAIL = os.environ.get("MAIL")
    PASS = os.environ.get("PASS")
    DIR = os.path.dirname(__file__)+"/../../static"
    @staticmethod
    def comment_cache_filepath(video_id):
        return Config.DIR + "/{}".format(video_id)
    @staticmethod
    def has_comment_cache(video_id):
        return os.path.isfile(Config.comment_cache_filepath(video_id))
    @staticmethod
    def comment_from_cache(video_id):
        with open(Config.comment_cache_filepath(video_id)) as f:
            return pickle.load(f)
    @staticmethod
    def set_comment_cache(video_id, data):
        with open(Config.comment_cache_filepath(video_id), "w+") as f:
            return pickle.dump(data, f)

    @staticmethod
    def videoinfo_cache_filepath(video_id):
        return Config.DIR + "/info/{}".format(video_id)
    @staticmethod
    def has_videoinfo_cache(video_id):
        return os.path.isfile(Config.videoinfo_cache_filepath(video_id))
    @staticmethod
    def videoinfo_from_cache(video_id):
        with open(Config.videoinfo_cache_filepath(video_id)) as f:
            return pickle.load(f)
    @staticmethod
    def set_videoinfo_cache(video_id, data):
        with open(Config.videoinfo_cache_filepath(video_id), "w+") as f:
            return pickle.dump(data, f)

    @staticmethod
    def videometa_cache_filepath(video_id):
        return Config.DIR + "/meta/{}".format(video_id)
    @staticmethod
    def has_videometa_cache(video_id):
        return os.path.isfile(Config.videometa_cache_filepath(video_id))
    @staticmethod
    def videometa_from_cache(video_id):
        with open(Config.videometa_cache_filepath(video_id)) as f:
            return pickle.load(f)
    @staticmethod
    def set_videometa_cache(video_id, data):
        with open(Config.videometa_cache_filepath(video_id), "w+") as f:
            return pickle.dump(data, f)


Browser = mechanize.Browser()
Browser.set_handle_robots(False)

class Comment:
    def __init__(self, text, date):
        self.text = self.normalize(text)
        self.date = date

    def cyclic_normalize(self, text):
        """
        (1,2,3,4)文字の連続を吸収
        e.g. wwwwww -> w
        """
        lasts = [" ", " ", "  ", "   ", "    "]
        i = 0
        ret = ""
        while i < len(text):
            ret += text[i]
            for j in range(1, len(lasts)):
                lasts[j] = lasts[j][1:]
                lasts[j] += text[i]
            while True:
                if text[i:i+1] == lasts[1]: i+=1
                elif text[i:i+2] == lasts[2]: i+=2
                elif text[i:i+3] == lasts[3]: i+=3
                elif text[i:i+4] == lasts[4]: i+=4
                else: break
        return ret


    def normalize(self, text):
        """
        正規化
        参考: http://d.hatena.ne.jp/torasenriwohashiru/20110806/1312558290
        """
        # 空白除去
        if text is None: return None
        unicode_normalized = unicodedata.normalize('NFKC', text)
        normalized = "".join(unicode_normalized.split())
        cyclic_normalized = self.cyclic_normalize(normalized)
        return cyclic_normalized

class VideoMeta:
    def __init__(self, video_id, title, description, comment_num, thumbnail_url, **lest_dict):
        self.video_id = video_id
        self.title = title
        self.description = description
        self.comment_num = comment_num
        self.thumbnail_url = thumbnail_url


class VideoInfo:
    def __init__(self, video_id, thread_id, ms, user_id, **lest_dict):
        # url = "http://flapi.nicovideo.jp/api/getflv/{}".format(video_id)
        self.video_id = video_id
        self.thread_id = thread_id
        self.ms = ms
        self.user_id = user_id
        threadkeyinfo = self.__getthreadkey()
        self.threadkey = threadkeyinfo["threadkey"]
        self.force_184 = threadkeyinfo["force_184"]
        self.waybackkey = self.__getwaybackkey()["waybackkey"]

    def comments(self, size=10):
        # cache
        if Config.has_comment_cache(video_id=self.video_id):
            # return Config.comment_from_cache(video_id=self.video_id)[:size]
            return Config.comment_from_cache(video_id=self.video_id) #キャッシュがあるときは全部使う

        def comments_generator():
            response = self.__fetch_comment()
            comments_soup = list(reversed(response.find("packet").findAll("chat")[:-2]))
            if len(comments_soup) == 0: raise StopIteration
            for chat in comments_soup:
                # print chat
                comment = Comment(chat.string, int(chat["date"]))
                if comment.text is None: continue
                yield comment

            while True:
                print(comment.date)
                response = self.__fetch_comment(date=comment.date)
                comments_soup = list(reversed(response.find("packet").findAll("chat")[:-2]))
                if len(comments_soup) == 0: raise StopIteration
                for chat in comments_soup:
                    comment = Comment(chat.string, int(chat["date"]))
                    if comment.text is None: continue
                    yield comment

        ret = list(itertools.islice(comments_generator(), 0, size))
        Config.set_comment_cache(self.video_id, ret)
        return ret




    def __fetch_comment(self, date=None):
        if date is None: date = int(time.time())
        xml = '''
        <thread
            thread="{0}"
            version="20061206"
            res_from="-1000"
            waybackkey="{1}"
            when="{2}"
            user_id="{3}"
            threadkey="{4}"
            scores="1"
            force_184="{5}"
        />
        '''.format(self.thread_id, self.waybackkey, date, self.user_id, self.threadkey, self.force_184)

        # print xml

        body = Browser.open(self.ms, xml).read()
        return BeautifulSoup(body)


    def __getwaybackkey(self):
        url = "http://flapi.nicovideo.jp/api/getwaybackkey?thread={}".format(self.thread_id)
        return self.__urlquoted2dict(Browser.open(url).read())

    def __getthreadkey(self):
        print(self.thread_id)
        url = "http://flapi.nicovideo.jp/api/getthreadkey?thread={}".format(self.thread_id)
        return self.__urlquoted2dict(Browser.open(url).read())

    def __urlquoted2dict(self, response_string):
        raw_list = [token.split("=") for token in response_string.split("&")]
        print(raw_list)
        unquoted_dict = dict([[k, urllib.parse.unquote(v)] for k,v in raw_list])
        return unquoted_dict


class Nicovideo:
    def __init__(self):
        self.browser = Browser
        self.log_in()

    def log_in(self):
        print("login")
        print(Config.MAIL)
        print(Config.PASS)
        self.browser.open("https://account.nicovideo.jp/login?site=niconico")
        # self.browser.open("https://secure.nicovideo.jp/secure/login?site=niconico")
        self.browser.select_form(nr=0)
        self.browser["mail_tel"]=Config.MAIL
        self.browser["password"]=Config.PASS
        self.browser.submit()


    def getvideoinfo(self, video_id):
        if Config.has_videoinfo_cache(video_id=video_id):
            return Config.videoinfo_from_cache(video_id=video_id)
        else:
            print("video id =",video_id)
            flvinfo = self.__getflvinfo(video_id)
            vinfo = VideoInfo(video_id, **flvinfo)
            Config.set_videoinfo_cache(video_id, vinfo)
            return vinfo

    def getvideometa(self, video_id):
        if Config.has_videometa_cache(video_id=video_id):
            return Config.videometa_from_cache(video_id=video_id)
        else:
            url = "http://ext.nicovideo.jp/api/getthumbinfo/{}".format(video_id)
            video_meta_soup = BeautifulSoup(self.browser.open(url).read())
            thumb_dict = {item.name: item.text for item in video_meta_soup.find("thumb").findChildren(recursive=False)}
            thumb_dict["video_id"] = video_id
            vmeta = VideoMeta(**thumb_dict)
            Config.set_videometa_cache(video_id, vmeta)
            return vmeta

    def __getflvinfo(self, video_id):
        url = "http://flapi.nicovideo.jp/api/getflv/{}".format(video_id)
        response_string = self.browser.open(url).readline()
        raw_list = [token.split("=") for token in response_string.split("&")]
        unquoted_dict = dict([[k, urllib.unquote(v)] for k,v in raw_list])
        print(unquoted_dict)
        return unquoted_dict


    def __htmlentity2unicode(self, text):
        # 正規表現のコンパイル
        reference_regex = re.compile(r'&(#x?[0-9a-f]+|[a-z]+);', re.IGNORECASE)
        num16_regex = re.compile(r'#x\d+', re.IGNORECASE)
        num10_regex = re.compile(r'#\d+', re.IGNORECASE)

        result = ''
        i = 0
        while True:
           # 実体参照 or 文字参照を見つける
           match = reference_regex.search(text, i)
           print("text")
           print(text)
           print("match", match)
           if match is None:
               result += text[i:]
               break

           result += text[i:match.start()]
           i = match.end()
           name = match.group(1)


           # 実体参照
           if name in list(html.entities.name2codepoint.keys()):
               result += chr(html.entities.name2codepoint[name])
           # 文字参照
           elif num16_regex.match(name):
               # 16進数
               result += chr(int('0'+name[1:], 16))
           elif num10_regex.match(name):
               # 10進数
               result += chr(int(name[1:]))
        return result