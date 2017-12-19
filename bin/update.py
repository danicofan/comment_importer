# -*- coding: utf-8 -*-
import sys
import os
import argparse
import collections
import tqdm

ROOTPATH = os.path.dirname(__file__) + "/.."
sys.path.append(ROOTPATH)
import nico_comment_import
import add_new_series


def load_danime():
    danime = nico_comment_import.danime.DAnimeService(os.path.join(ROOTPATH, "data"))

    video_index = {}
    for series in danime.series:
        for video in series.videos:
            video_index[video.danime_content["contentId"]] = series.title
    return danime, video_index


def update(args):
    danime, video_index = load_danime()

    tag_collections = collections.defaultdict(list)

    search = nico_comment_import.NiconicoSearch()
    for video in tqdm.tqdm(search.search_tags_exact(
            ["dアニメストア"], limit=200000,
            additional_params={
                "filters[channelId][0]": "2632720"
            }

    ), desc="search all"):
        # print video
        # print video.keys()
        # print video["channelId"]
        for tag in video["tags"].split()[:]:
            tag_collections[tag].append(video)

    for tag, videos in sorted(tag_collections.items(), key=(lambda kv: - len(kv[1]))):
        print tag.encode("utf-8")
        for video in videos:
            if video["contentId"] in video_index:
                break
            if len(videos) > 100:
                break
        else:
            a = collections.namedtuple('a',
                                       'series search_title_ambiguous offset cutlast query_head force remove_wa remove_regexp exact_regexp remove_title ambiguous_wa greek_number grep_filter grep_filter_ignore remove_head')
            # print tag.encode("utf-8")
            if tag.find("_") > 0:
                query_heads = (None,)
            else:
                query_heads = (None, 2)
            for remove_wa in (False, True):
                for query_head in query_heads:
                    add_new_series.main(a(
                        series=tag.encode("utf-8"),
                        search_title_ambiguous=False,
                        offset=0,
                        cutlast=0,
                        query_head=query_head,
                        force=True,
                        remove_wa=remove_wa,
                        remove_head=None,
                        remove_regexp=None,
                        exact_regexp=[],
                        remove_title=False,
                        ambiguous_wa=False,
                        greek_number=False,
                        grep_filter=None,
                        grep_filter_ignore=None
                    ))
            danime, video_index = load_danime()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    update(args)
