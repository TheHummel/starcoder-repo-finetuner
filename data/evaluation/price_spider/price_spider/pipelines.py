# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
from collections import defaultdict


class PricePipeline:
    def __init__(self):
        self.files = defaultdict(list)

    def process_item(self, item, spider):
        if "price" in item and item["price"]:
            price = (
                item["price"][0] if isinstance(item["price"], list) else item["price"]
            )
            item["price"] = (
                price.replace("EUR ", "").replace("eur ", "").replace(",", ".").strip()
            )
        site = item.get("site", "unknown")
        if isinstance(site, list):
            site = "_".join(site)
        self.files[site].append(dict(item))
        spider.logger.debug(
            f"Processed item for {site}, total items: {len(self.files[site])}"
        )
        return item

    def close_spider(self, spider):
        spider.logger.info(f"Closing spider, writing files: {dict(self.files)}")
        for site, items in self.files.items():
            if items:
                with open(f"price_{site}.json", "w", encoding="utf-8") as f:
                    json.dump(items, f, indent=2)
                spider.logger.info(f"Wrote {len(items)} items to price_{site}.json")
            else:
                spider.logger.warning(f"No items to write for {site}")
