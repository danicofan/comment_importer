# -*- coding: utf-8 -*-
import sys
import os
import argparse
import random

import time
import tqdm

sys.path.append(os.path.dirname(__file__) + "/..")
import nico_comment_import


def import_comment(original_video, target_video, min_count=3, force=False, offset=0, cutlast=0):
    nicovideo = nico_comment_import.NicovideoSevice(nico_comment_import.Config())
    original_video = nicovideo.get_vieo(original_video)
    target_video = nicovideo.get_vieo(target_video)

    if abs(original_video.flv_info.length + offset - cutlast - target_video.flv_info.length) > 1:
        print "two videos have different length"
        print original_video.flv_info.length, original_video.meta.title
        print target_video.flv_info.length, target_video.meta.title

        return False

        k = raw_input("force?")
        print k
        if k != "y":
            return False

    print(original_video.meta.title)
    print(target_video.meta.title)

    if not force:
        k = raw_input("ok?")
        print k
        if k != "y":
            exit(1)

    filter = nico_comment_import.CommentFilter(
        original_video,
        target_video,
        limit=10000,
    )

    comments = list(filter.get_filtered_comments(min_count=min_count, window=5))
    for comment in comments:
        print(comment.original_text)

    for comment in tqdm.tqdm(comments):
        if vpos / 100 > (original_video.flv_info.length - cutlast):
            continue
        time.sleep(5)
        vpos = comment.vpos + offset + int((random.random() * 1.5 - 0.5) * 100)  # [-0.5, 1]秒ずらす。あとから同じコメントが来ても変じゃないように
        vpos = max(vpos, 0)
        target_video.post_comment(vpos, comment.original_text.encode("utf-8"))
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("original_video")
    parser.add_argument("target_video")
    args = parser.parse_args()
    import_comment(args.original_video, args.target_video)
