# -*- coding: utf-8 -*-
import argparse

import os
import urllib2

import sys
import time

sys.path.append(os.path.dirname(__file__) + "/..")
import nico_comment_import

import import_comment
import re
import random


def main(args):
    search = nico_comment_import.NiconicoSearch()
    for ditem in search.search_tags_exact(["dアニメストア", args.series]):
        if args.grep_filter is not None:
            if not re.search(args.grep_filter.decode("utf-8"), ditem['title']):
                continue
        if args.grep_filter_ignore is not None:
            print re.search(args.grep_filter_ignore.decode("utf-8"), ditem['title'])
            if re.search(args.grep_filter_ignore.decode("utf-8"), ditem['title']):
                continue

        query = ditem['title'].replace(u"／", " ").replace(u"？", " ")
        query = query.replace(u"【日テレオンデマンド】", " ")
        query = query.replace(u"II", u"Ⅱ")
        query = query.replace(u"III", u"Ⅲ")
        query = query.replace(u"IV", u"Ⅳ")
        query = query.replace(u"V", u"Ⅴ")
        query = query.replace(u"VI", u"Ⅵ")
        query = query.replace(u"VII", u"Ⅶ")
        query = query.replace(u"Ｉ", u"Ⅰ")
        query = query.replace(u"ＩＩ", u"Ⅱ")
        query = query.replace(u"ＩＩＩ", u"Ⅲ")
        query = query.replace(u"ＩＶ", u"Ⅳ")
        query = query.replace(u"Ｖ", u"Ⅴ")
        query = query.replace(u"ＶＩ", u"Ⅵ")
        query = query.replace(u"ＶＩＩ", u"Ⅶ")
        query = query.replace(u"ＶＩＩＩ", u"Ⅷ")
        query = query.replace(u"ＩＸ", u"Ⅸ")
        query = query.replace(u"Ｘ", u"Ⅹ")

        if args.remove_regexp:
            for regexp in args.remove_regexp:
                query = re.sub(regexp.decode("utf-8"), "", query)
        if args.remove_wa:
            query = re.sub(u"第.*話", "", query)
        if args.remove_title:
            query = " ".join(query.split()[1:])  # 最初の文節を除去
        print(query)

        for item in search.search_title(query):
            if (ditem['contentId'] == item['contentId']):
                continue

            print(item['title'])
            print("cooldown...")
            time.sleep(30)  # 連続アクセス規制
            try:
                result = import_comment.import_comment(item['contentId'], ditem['contentId'], min_count=args.min_count,
                                                       force=args.force, offset=args.offset, cutlast=args.cutlast)
                if result: break
            except AssertionError as e:
                print e
            except urllib2.HTTPError as e:
                if e.code == 404:  # 原因不明
                    print e
                else:  # 基本連続アクセス
                    print e
                    time.sleep(random.randint(30, 180))  # 連続アクセス規制
                    result = import_comment.import_comment(item['contentId'], ditem['contentId'],
                                                           min_count=args.min_count,
                                                           force=args.force, offset=args.offset, cutlast=args.cutlast)
                    if result: break


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("series")
    parser.add_argument("min_count", type=int)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--cutlast", type=int, default=0)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--remove_wa", action="store_true")
    parser.add_argument("--remove_regexp", nargs="+")
    parser.add_argument("--remove_title", action="store_true")
    parser.add_argument("--grep_filter")
    parser.add_argument("--grep_filter_ignore")
    args = parser.parse_args()
    main(args)
