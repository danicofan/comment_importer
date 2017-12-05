# -*- coding: utf-8 -*-
import os


class Config(object):
    def __init__(self):
        self.mail = os.environ.get("MAIL")
        self.passwd = os.environ.get("PASS")
