# -*- coding: utf-8 -*-
import json

import os
from pykakasi import kakasi


class DAnimeVideo(object):
    def __init__(self, danime_content, channel_content, offset, cutlast):
        self.cutlast = cutlast
        self.offset = offset
        self.channel_content = channel_content
        self.danime_content = danime_content

    def dump(self):
        json = self.danime_content
        json["offset"] = self.offset
        json["cutlast"] = self.cutlast
        json["channel_content"] = self.channel_content
        return json


class DAnimeSeries(object):
    def __init__(self, title):
        self.title = title
        self.videos = []

    def add_video(self, video):
        self.videos.append(video)

    def save(self, directory):
        filename = self.__kakashi_convert(self.title.decode("utf-8")) + ".json"
        path = os.path.join(directory, filename)
        with open(path, "w+") as f:
            json.dump({
                "title": self.title,
                "videos": [video.dump() for video in self.videos]
            }, f, indent=2)

    def __kakashi_convert(self, text):
        kakasi_service = kakasi()
        kakasi_service.setMode("H", "a")  # default: Hiragana no convert
        kakasi_service.setMode("K", "a")  # default: Katakana no convert
        kakasi_service.setMode("J", "a")  # default: Japanese no convert
        conv = kakasi_service.getConverter()
        result = conv.do(text)
        return result


class DAnimeService(object):
    def __init__(self, directory):
        self.directory = directory

    def add_series(self, series):
        """
        :type series: DAnimeSeries
        """
        series.save(self.directory)
