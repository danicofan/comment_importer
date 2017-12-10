# -*- coding: utf-8 -*-
import json

import os
from pykakasi import kakasi


class DAnimeVideo(object):
    def __init__(self):
        pass


class DAnimeSeries(object):
    def __init__(self, title):
        self.title = title

    def save(self, directory):
        filename = self.__kakashi_convert(self.title.decode("utf-8")) + ".json"
        path = os.path.join(directory, filename)
        with open(path, "w+") as f:
            json.dump({
                "title": self.title
            }, f)

    def __kakashi_convert(self, text):
        kakasi_service = kakasi()
        kakasi_service.setMode("H", "a")  # default: Hiragana no convert
        kakasi_service.setMode("K", "a")  # default: Katakana no convert
        kakasi_service.setMode("J", "a")  # default: Japanese no convert
        # kakasi.setMode("E", "a")  # default: Symbols no convert
        # kakasi.setMode("r", "Hepburn")  # default: use Hepburn Roman table
        # kakasi.setMode("s", True)  # separate, default: no Separator
        # kakasi.setMode("C", True)  # capitalize default: no Capitalize
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
