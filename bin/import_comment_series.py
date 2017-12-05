# -*- coding: utf-8 -*-
import argparse

import os
import sys

sys.path.append(os.path.dirname(__file__) + "/..")
import nico_comment_import

import import_comment

def main(args):
    search = nico_comment_import.NiconicoSearch()
    for ditem in search.search_tags_exact(["dアニメストア", args.series]):
        print(ditem['title'])
        for item in search.search_title(ditem['title']):
            print(item['title'])
            import_comment.import_comment(item['contentId'], ditem['contentId'])
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("series")
    args = parser.parse_args()
    main(args)
