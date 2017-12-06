# -*- coding: utf-8 -*-
import argparse

import os
import sys
import time

sys.path.append(os.path.dirname(__file__) + "/..")
import nico_comment_import

import import_comment

def main(args):
    search = nico_comment_import.NiconicoSearch()
    for ditem in search.search_tags_exact(["dアニメストア", args.series]):
        print(ditem['title'])
        for item in search.search_title(ditem['title']):
            print(item['title'])
            print("cooldown...")
            time.sleep(30) # 連続アクセス規制
            try:
                import_comment.import_comment(item['contentId'], ditem['contentId'], min_count=args.min_count, force=args.force)
                break
            except AssertionError as e:
                print e


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("series")
    parser.add_argument("min_count", type=int)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    main(args)
