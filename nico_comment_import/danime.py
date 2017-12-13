# -*- coding: utf-8 -*-
import glob
import json

import os
import time
import unicodedata

from pykakasi import kakasi


class DAnimeVideo(object):
    def __init__(self, danime_content, channel_content, offset, cutlast, comment_imported=False):
        self.cutlast = cutlast
        self.offset = offset
        self.channel_content = channel_content
        self.danime_content = danime_content
        self.comment_imported = comment_imported

    def dump(self):
        json = self.danime_content
        json["commentImported"] = self.comment_imported
        if self.channel_content is not None:
            json["offset"] = self.offset
            json["cutlast"] = self.cutlast
            json["channelContent"] = self.channel_content
        return json

    @staticmethod
    def load(json):
        if "channelContent" in json:
            return DAnimeVideo(json, json["channelContent"], json["offset"], json["cutlast"], json["commentImported"])
        else:
            return DAnimeVideo(json, None, 0, 0, json["commentImported"])


class DAnimeSeries(object):
    def __init__(self, title):
        self.title = title
        self.videos = []
        self.first_appeared = int(time.time())

    def add_video(self, video):
        for i in range(len(self.videos)):
            if self.videos[i].danime_content["contentId"] == video.danime_content["contentId"]:
                self.videos[i] = video
                break
        else:
            self.videos.append(video)

    def save(self, directory):
        assert isinstance(self.title, unicode)
        filename = self.__kakashi_convert(self.title) + ".json"
        path = os.path.join(directory, filename)
        with open(path, "w+") as f:
            json.dump({
                "title": self.title,
                "firstAppeared": self.first_appeared,
                "videos": [video.dump() for video in self.videos]
            }, f, indent=2)

    @staticmethod
    def load(path):
        with open(path) as f:
            json_data = json.load(f)
            series = DAnimeSeries(json_data["title"])
            series.first_appeared = json_data["firstAppeared"]
            series.videos = [DAnimeVideo.load(video) for video in json_data["videos"]]
            return series

    def __kakashi_convert(self, text):
        text = unicodedata.normalize("NFKC", text)
        kakasi_service = kakasi()
        kakasi_service.setMode("H", "a")  # default: Hiragana no convert
        kakasi_service.setMode("K", "a")  # default: Katakana no convert
        kakasi_service.setMode("J", "a")  # default: Japanese no convert
        conv = kakasi_service.getConverter()
        result = conv.do(text).encode("utf-8")
        result = "".join([c for c in result if c.isalnum()])
        return result

    def search_video_by_content_id(self, content_id):
        for video in self.videos:
            if video.danime_content['contentId'] == content_id:
                return video
        else:
            return None


class DAnimeService(object):
    def __init__(self, directory):
        self.directory = directory
        self.series = [
            DAnimeSeries.load(path) for path in glob.glob(os.path.join(self.directory, '*.json'))
        ]
        self.title_index = dict([(series.title, series) for series in self.series])

    def add_series(self, series):
        """
        :type series: DAnimeSeries
        """
        series.save(self.directory)

    def search_series_by_title(self, title):
        if title in self.title_index:
            return self.title_index[title]
        else:
            return None
