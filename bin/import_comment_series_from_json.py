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
    series = nico_comment_import.danime.DAnimeSeries.load(args.path)
    for video in series.videos:
        print(video.danime_content['title'])
        print("cooldown...")
        time.sleep(30)  # 連続アクセス規制

        if video.channel_content is not None:
            nico_comment_import.utility.retry_call(
                lambda: import_comment.import_comment(video.channel_content['contentId'], video.danime_content['contentId'],
                                                      min_count=args.min_count,
                                                      force=args.force, offset=video.danime_content['offset'], cutlast=video.danime_content['cutlast']),
                random_time=300, max_retry=5
            )
            video.comment_imported = True
            series.add_video(video)
    danime = nico_comment_import.danime.DAnimeService(os.path.join(ROOTPATH, "data"))
    danime.add_series(series)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("min_count", type=int)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    main(args)
