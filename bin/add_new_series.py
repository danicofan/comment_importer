# -*- coding: utf-8 -*-
import argparse

import os
import urllib2

import sys
import time

ROOTPATH = os.path.dirname(__file__) + "/.."
sys.path.append(ROOTPATH)
import nico_comment_import

import import_comment
import re
import random


def main(args):
    search = nico_comment_import.NiconicoSearch()
    print(args.series)
    danime = nico_comment_import.danime.DAnimeService(os.path.join(ROOTPATH, "data"))

    series = danime.search_series_by_title(args.series.decode("utf-8"))
    if series is None:
        series = nico_comment_import.danime.DAnimeSeries(args.series.decode("utf-8"))

    for ditem in search.search_tags_exact(["dアニメストア", args.series]):
        if args.grep_filter is not None:
            if not re.search(args.grep_filter.decode("utf-8"), ditem['title']):
                continue
        if args.grep_filter_ignore is not None:
            print re.search(args.grep_filter_ignore.decode("utf-8"), ditem['title'])
            if re.search(args.grep_filter_ignore.decode("utf-8"), ditem['title']):
                continue

        # 登録済みか
        existing_video = series.search_video_by_content_id(ditem['contentId'])
        # print existing_video.danime_content['contentId']
        # print existing_video.danime_content['title']
        if (existing_video is not None) and (existing_video.channel_content is not None):
            continue
        else:
            print existing_video
            print ditem['title']
            print ditem['contentId']

        query = ditem['title'].replace(u"／", " ").replace(u"？", " ")
        query = query.replace(u"【日テレオンデマンド】", " ")
        query = query.replace(u"IV", u"Ⅳ")
        query = query.replace(u"VII", u"Ⅶ")
        query = query.replace(u"VI", u"Ⅵ")
        query = query.replace(u"V", u"Ⅴ")
        query = query.replace(u"III", u"Ⅲ")
        query = query.replace(u"II", u"Ⅱ")
        query = query.replace(u"ＩＶ", u"Ⅳ")
        query = query.replace(u"ＶＩＩＩ", u"Ⅷ")
        query = query.replace(u"ＶＩＩ", u"Ⅶ")
        query = query.replace(u"ＶＩ", u"Ⅵ")
        query = query.replace(u"Ｖ", u"Ⅴ")
        query = query.replace(u"ＩＸ", u"Ⅸ")
        query = query.replace(u"Ｘ", u"Ⅹ")
        query = query.replace(u"ＩＩＩ", u"Ⅲ")
        query = query.replace(u"ＩＩ", u"Ⅱ")
        query = query.replace(u"Ｉ", u"Ⅰ")

        if args.remove_regexp:
            for regexp in args.remove_regexp:
                query = re.sub(regexp.decode("utf-8"), "", query)
        if args.remove_wa:
            query = re.sub(u"第.*話", "", query)
        elif not args.ambiguous_wa: # strict match
            query = re.sub(u"(第.*話)", r'"\1"', query)

        if args.remove_title:
            query = " ".join(query.split()[1:])  # 最初の文節を除去

        if args.query_head is not None:
            query = " ".join(query.split()[:args.query_head])

        for item in search.search_title(query):
            if (ditem['contentId'] == item['contentId']):
                continue

            if abs(int(item['lengthSeconds']) - args.offset - args.cutlast - ditem['lengthSeconds']) > 1:
                print "two videos have different length"
                print ditem['lengthSeconds'], ditem['title']
                print item['lengthSeconds'], item['title']
            else:
                series.add_video(
                    nico_comment_import.danime.DAnimeVideo(ditem, item, args.offset, args.cutlast)
                )
                break
        else:
            series.add_video(
                nico_comment_import.danime.DAnimeVideo(ditem, None, args.offset, args.cutlast)
            )
    print "VVVVVV 確認 VVVVVV"
    for video in series.videos:
        print "=======\n{}\n{}".format(
            video.danime_content['title'].encode("utf-8"),
            video.channel_content['title'].encode("utf-8") if video.channel_content is not None else "なし" )
    k = raw_input("ok?")
    print k
    if k != "y":
        exit(1)
    else:
        danime.add_series(series)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("series")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--cutlast", type=int, default=0)
    parser.add_argument("--query_head", type=int)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--remove_wa", action="store_true")
    parser.add_argument("--remove_regexp", nargs="+")
    parser.add_argument("--remove_title", action="store_true")
    parser.add_argument("--ambiguous_wa", action="store_true")
    parser.add_argument("--grep_filter")
    parser.add_argument("--grep_filter_ignore")
    args = parser.parse_args()
    main(args)
