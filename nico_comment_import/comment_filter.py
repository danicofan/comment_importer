# -*- coding: utf-8 -*-

import collections
import nico_comment_import
import time


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
        print "channel_comments: ", len(counter)

        burst_count = 0
        for comments in counter.values():
            if len(comments) <= min_count:
                continue
                # 頻度が低い。弾幕ではない

            burst = self.find_burst(comments, window, min_count)
            if burst is None:
                continue
                # burstではない

            if burst.text in target_comments:
                continue
                # 既に移植済み

            if burst.text.find(u"見納め") >= 0:
                continue
                # 見納めコメントは。。。

            if burst.text.find(u"何が良いの") >= 0:
                continue
                # 煽り

            if burst.text.find(u"荒") >= 0:
                continue
                # 煽り

            if burst.text.find(u"売名") >= 0:
                continue
                # 煽り

            if burst.text.find(u"右クリック") >= 0:
                continue
                # 煽り

            if burst.text.find(u"ミリオン") >= 0:
                continue
                # ミリオン祝は。。。

            burst_count += 1
            yield burst
        if burst_count > 10:
            for comment in list(target_comments):
                if comment.find(u"チャンネルから") >= 0:
                    break
            else:
                yield nico_comment_import.Comment(text=u"チャンネルから少しコメント移植してみました", date=time.time(), vpos=100)

    def find_burst(self, comments, window, min_count):
        """
        同じコメントがバーストしてる位置を探す。なければNone
        """
        maxcount = 0
        for candidate_comment in comments:
            count = 0
            for comment in comments:
                # windowサイズ内に入るコメント数
                if comment.vpos >= candidate_comment.vpos and comment.vpos <= candidate_comment.vpos + window * 100:
                    count += 1
            maxcount = max(maxcount, count)  # 最大弾幕サイズ
        if maxcount < min_count:
            return None
        for candidate_comment in comments:
            count = 0
            for comment in comments:
                if comment.vpos >= candidate_comment.vpos and comment.vpos <= candidate_comment.vpos + window * 100:
                    count += 1
            if count > int(maxcount * 0.8):  # 先頭20%
                return candidate_comment
