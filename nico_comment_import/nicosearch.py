# -*- coding: utf-8 -*-
import requests


class NiconicoSearch(object):
    def search_title(self, title):
        params = {
            "targets": "title",
            "fields": "contentId,title,viewCounter,thumbnailUrl,tags,description,startTime,lengthSeconds",
            "_sort": "-viewCounter",
            "_context": "apiguide_application",
            "q": title,
        }

        r = requests.get(
            url='http://api.search.nicovideo.jp/api/v2/snapshot/video/contents/search',
            params=params
        )
        for item in r.json()["data"]:
            yield item

    def search_tags_base(self, target, tags, additional_params=dict(), limit=100):
        """
        人気順にタグ検索
        """
        for offset in range(0, limit, 100):
            each_limit = min(limit - offset, 100)
            params = {
                "targets": target,
                "fields": "contentId,title,viewCounter,thumbnailUrl,tags,description,startTime,lengthSeconds",
                "_sort": "-viewCounter",
                "_offset": offset,
                "_limit": each_limit,
                "_context": "apiguide_application",
                "q": " ".join(tags),
            }
            params.update(additional_params)

            r = requests.get(
                url='http://api.search.nicovideo.jp/api/v2/snapshot/video/contents/search',
                params=params
            )
            for item in r.json()["data"]:
                yield item

    def search_tags(self, tags, limit=100):
        return self.search_tags_base(target="tags", tags=tags, additional_params={}, limit=limit)

    def search_tags_exact(self, tags, limit=100):
        return self.search_tags_base(target="tags_exact", tags=tags, additional_params={}, limit=limit)

    def search_category_tag(self, tag, limit=100):
        return self.search_tags_base(target="tags_exact", tags=[tag],
                                     additional_params={"filters[categoryTags][0]": tag},
                                     limit=limit)
