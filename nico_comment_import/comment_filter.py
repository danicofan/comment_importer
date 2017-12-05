# -*- coding: utf-8 -*-

import collections


class CommentFilter(object):
    """
    弾幕コメントだけに絞るフィルタ
    """

    def __init__(self, original_video, target_video, limit):
        self.limit = limit
        self.target_video = target_video
        self.original_video = original_video

    def get_filtered_comments(self, min_count, window=5):
        target_comments = set(comment.text for comment in self.target_video.get_comments(self.limit))

        counter = collections.defaultdict(list)
        for comment in self.original_video.get_comments(self.limit):
            counter[comment.text].append(comment)
        for comments in counter.values():
            if len(comments) <= min_count:
                continue
                # 頻度が低い。弾幕ではない

            burst = self.find_burst(comments, window)
            if burst is None:
                continue
                #burstではない

            if burst.text in target_comments:
                continue
                # 既に移植済み

            if burst.text == u"見納め":
                continue
                # 見納めコメントはうざい

            yield burst

    def find_burst(self, comments, window):
        """
        同じコメントがバーストしてる市を探す。なければNone
        """
        for candidate_comment in comments:
            for comment in comments:
                if comment.vpos >= candidate_comment.vpos and comment.vpos <= candidate_comment.vpos + window:
                    return candidate_comment
