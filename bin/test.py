# -*- coding: utf-8 -*-
import sys
import os
import argparse
import random

import time
import tqdm

sys.path.append(os.path.dirname(__file__) + "/..")
import nico_comment_import


def import_comment(original_video, target_video, min_count=3, force=False):
    nicovideo = nico_comment_import.NicovideoSevice(nico_comment_import.Config())
    original_video = nicovideo.get_vieo(original_video)
    target_video = nicovideo.get_vieo(target_video)

    t = u"チャンネルから少しコメント移植してみました"
    # t = u"UMR"
    target_video.post_comment(100, t.encode("utf-8"))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("original_video")
    parser.add_argument("target_video")
    args = parser.parse_args()
    import_comment(args.original_video, args.target_video)
