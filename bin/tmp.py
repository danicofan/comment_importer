# -*- coding: utf-8 -*-
import json
import glob

import os
import sys
import json
import time

sys.path.append(os.path.dirname(__file__) + "/..")
import nico_comment_import

for path in glob.glob("data/*.json"):
    with open(path) as f:
        data = json.load(f)
        data["firstAppeared"] = int(time.time())
        for video in data["videos"]:
            video["commentImported"] = False
            if "channel_content" in video:
                c = video["channel_content"]
                del video["channel_content"]
                video["channelContent"] = c
    with open(path, "w") as f:
        json.dump(data, f)
