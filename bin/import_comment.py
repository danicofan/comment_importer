# -*- coding: utf-8 -*-
import sys
import os
import argparse

import time

sys.path.append(os.path.dirname(__file__) + "/..")
import nico_comment_import


def main(args):
    nicovideo = nico_comment_import.NicovideoSevice(nico_comment_import.Config())
    original_video = nicovideo.get_vieo(args.original_video)
    target_video = nicovideo.get_vieo(args.target_video)

    assert original_video.flv_info.length == target_video.flv_info.length
    print(original_video.meta.title)
    print(target_video.meta.title)

    k = raw_input("ok?")
    print k
    if k != "y":
        exit(1)

    filter = nico_comment_import.CommentFilter(
        original_video,
        target_video,
        limit=10000,
    )

    comments = list(filter.get_filtered_comments(min_count=5, window=5))
    for comment in comments:
        print(comment.original_text)

    # k = raw_input("ok?")
    # print k
    # if k != "y":
    #     exit(1)

    for comment in comments:
        time.sleep(5)
        target_video.post_comment(comment.vpos, comment.original_text.encode("utf-8"))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("original_video")
    parser.add_argument("target_video")
    args = parser.parse_args()
    main(args)
