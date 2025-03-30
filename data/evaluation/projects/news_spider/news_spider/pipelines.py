# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import json
from collections import defaultdict


class TopicPipeline:
    def __init__(self):
        self.files = defaultdict(list)

    def process_item(self, item, spider):
        if "topic" in item and type(item["topic"]) == str:
            item["topic"] = item["topic"].lower().strip()
        elif (
            "topic" in item and type(item["topic"]) == list and len(item["topic"]) == 1
        ):
            item["topic"] = item["topic"][0].lower().strip()
        site = item.get("site", "unknown")
        # Ensure site is a string, not a list
        if isinstance(site, list):
            spider.logger.error(f"Site is a list: {site}, using first element")
            site = site[0] if site else "unknown"
        self.files[site].append(dict(item))
        return item

    def close_spider(self, spider):
        for site, items in self.files.items():
            with open(f"news_{site}.json", "w", encoding="utf-8") as f:
                json.dump(items, f, indent=2)
