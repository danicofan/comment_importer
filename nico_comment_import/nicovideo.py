# -*- coding: utf-8 -*-
import itertools
import urllib
import urllib2

import mechanize
import unicodedata

import time

import re
from bs4 import BeautifulSoup


class Comment(object):
    def __init__(self, text, date, vpos):
        self.original_text = text
        self.text = self.normalize(text)
        self.date = date
        self.vpos = vpos

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
                if text[i:i + 1] == lasts[1]:
                    i += 1
                elif text[i:i + 2] == lasts[2]:
                    i += 2
                elif text[i:i + 3] == lasts[3]:
                    i += 3
                elif text[i:i + 4] == lasts[4]:
                    i += 4
                else:
                    break
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


class VideoMeta(object):
    def __init__(self, browser, video_id):
        self.browser = browser
        self.video_id = video_id

        meta_dict = self.getvideometa(self.video_id)
        self.title = meta_dict['title']
        self.description = meta_dict['description']
        self.comment_num = int(meta_dict['comment_num'])
        self.thumbnail_url = meta_dict['thumbnail_url']

    def getvideometa(self, video_id):
        url = "http://ext.nicovideo.jp/api/getthumbinfo/{}".format(video_id)
        video_meta_soup = BeautifulSoup(self.browser.open(url).read(), "html.parser")
        thumb_dict = {item.name: item.text for item in video_meta_soup.find("thumb").findChildren(recursive=False)}
        return thumb_dict


class VideoFLVInfo(object):
    def __init__(self, browser, video_id):
        self.browser = browser
        self.video_id = video_id

        self.info = self.__getflvinfo(video_id)
        # print(self.info)
        self.thread_id = self.info['thread_id']
        self.user_id = self.info['user_id']
        self.length = int(self.info['l'])
        self.ms = self.info['ms']
        self.is_premium = int(self.info['is_premium'])

    def __getflvinfo(self, video_id):
        url = "http://flapi.nicovideo.jp/api/getflv/{}".format(video_id)
        response_string = self.browser.open(url).readline()
        raw_list = [token.split("=") for token in response_string.split("&")]
        unquoted_dict = dict([[k, urllib.unquote(v)] for k, v in raw_list])
        return unquoted_dict


class Video(object):
    def __init__(self, browser, video_id):
        self.browser = browser
        self.video_id = self.__trueid(video_id)
        self.meta = VideoMeta(browser, self.video_id)
        self.flv_info = VideoFLVInfo(browser, self.video_id)

        threadkeyinfo = self.__getthreadkey()
        if not threadkeyinfo is None:
            self.threadkey = threadkeyinfo["threadkey"]
            self.force_184 = threadkeyinfo["force_184"]
            self.waybackkey = self.__getwaybackkey()["waybackkey"]

            self.__get_ticket()

    def __trueid(self, video_id):
        return self.__getnicoid(self.__getredirect("http://www.nicovideo.jp/watch/{}".format(video_id)))

    def __getredirect(self, url):
        self.browser.open(url)
        return self.browser.geturl()

    def __getnicoid(self, url):
        nicoid = re.search('([snmol0-9]*[0-9]+)', url).groups()[0]
        return nicoid

    def __get_ticket(self):
        response = self.__fetch_comment()
        return response.find("packet").find("thread")['ticket']

    def get_comments(self, size=10):
        def comments_generator():
            response = self.__fetch_comment()
            comments_soup = list(reversed(response.find("packet").findAll("chat")))
            if len(comments_soup) == 0:
                raise StopIteration
            for chat in comments_soup:
                comment = Comment(chat.string, int(chat["date"]), int(chat["vpos"]))
                if comment.text is None: continue
                yield comment

            while True:
                response = self.__fetch_comment(date=comment.date)
                comments_soup = list(reversed(response.find("packet").findAll("chat")))
                if len(comments_soup) == 0:
                    raise StopIteration
                for chat in comments_soup:
                    comment = Comment(chat.string, int(chat["date"]), int(chat["vpos"]))
                    if comment.text is None: continue
                    yield comment

        ret = list(itertools.islice(comments_generator(), 0, size))
        return ret

    def post_comment(self, vpos, text):
        response = self.__post_comment(vpos, text, comment_count=0)
        if response["status"] != "0":
            response = self.__post_comment(vpos, text, comment_count=int(response["no"])+1)
        if response["status"] != "0":
            time.sleep(20)
            response = self.__post_comment(vpos, text, comment_count=int(response["no"]) + 1)
        if response["status"] != "0":
            raise Exception("couldn't post comment")

    def __post_comment(self, vpos, text, comment_count):
        postkey = self.__getpostkey(comment_count)
        xml = '''
        <chat thread="{thread_id}" 
          ticket="{ticket}" 
          user_id="{user_id}" 
          vpos="{vpos}" 
          mail="{command}" 
          postkey="{post_key}" 
          premium="{premium}"
         >
         {text}
        </chat>
        '''.format(
            ticket=self.__get_ticket(),
            thread_id=self.flv_info.thread_id,
            user_id=self.flv_info.user_id,
            vpos=vpos,
            command="",
            post_key=postkey,
            premium=self.flv_info.is_premium,
            text=text
        )

        request = mechanize.Request(
            self.flv_info.ms,
            data=xml,
        )
        request.add_header('Content-Type', 'application/xml')

        response = self.browser.open(
            request
        ).read()
        res = BeautifulSoup(response, "html.parser").find("packet").find("chat_result")
        return res

    def __fetch_comment(self, date=None):
        if date is None:
            date = int(time.time()) + 10
        url = "{ms}thread?thread={thread_id}&version=20061206&res_from=-1000&scores=1&waybackkey={waybackkey}&threadkey={thread_key}&force_184={force_184}&user_id={user_id}&when={date}".format(
            ms=self.flv_info.ms,
            thread_id=self.flv_info.thread_id,
            thread_key=self.threadkey,
            waybackkey=self.waybackkey,
            date=date,
            user_id=self.flv_info.user_id,
            force_184=self.force_184)
        body = self.browser.open(url).read()
        return BeautifulSoup(body, "html.parser")

    def __getwaybackkey(self):
        url = "http://flapi.nicovideo.jp/api/getwaybackkey?thread={}".format(self.flv_info.thread_id)
        return self.__urlquoted2dict(self.browser.open(url).read())

    def __getthreadkey(self):
        url = "http://flapi.nicovideo.jp/api/getthreadkey?thread={}".format(self.flv_info.thread_id)
        try:
            return self.__urlquoted2dict(self.browser.open(url).read())
        except ValueError:
            print "Maybe, not a channel's video"
            return None

    def __urlquoted2dict(self, response_string):
        raw_list = [token.split("=") for token in response_string.split("&")]
        unquoted_dict = dict([[k, urllib.unquote(v)] for k, v in raw_list])
        return unquoted_dict

    def __getpostkey(self, comment_count=0):
        url = "http://flapi.nicovideo.jp/api/getpostkey/?version=1&yugi=&device=1&block_no={block_no}&thread={thread_id}&version_sub=2".format(
            thread_id=self.flv_info.thread_id,
            block_no=comment_count // 100
        )
        d = self.__urlquoted2dict(self.browser.open(url).read())
        return d["postkey"]


class NicovideoSevice(object):
    def __init__(self, config):
        self.browser = mechanize.Browser()
        self.browser.set_handle_robots(False)
        self.config = config
        self.__log_in()

    def __log_in(self):
        print("login")
        self.browser.open("https://account.nicovideo.jp/login?site=niconico")
        self.browser.select_form(nr=0)
        self.browser["mail_tel"] = self.config.mail
        self.browser["password"] = self.config.passwd
        self.browser.submit()

    def get_vieo(self, video_id):
        return Video(self.browser, video_id)
