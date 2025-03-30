# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
from collections import defaultdict


class StockSpiderPipeline:
    def __init__(self):
        self.stocks = defaultdict(list)

    def process_item(self, item, spider):
        isin = item.get("isin", "unknown")
        self.stocks[isin].append(dict(item))
        spider.logger.debug(
            f"Processed item for ISIN {isin}, total: {len(self.stocks[isin])}"
        )
        return item

    def close_spider(self, spider):
        all_stocks = []
        for isin, items in self.stocks.items():
            all_stocks.extend(items)
        spider.logger.info(
            f"Closing spider, items to write: {len(all_stocks)}, data: {all_stocks}"
        )
        if all_stocks:
            try:
                with open("stock_prices.json", "w", encoding="utf-8") as f:
                    json.dump(all_stocks, f, indent=2)
                spider.logger.info(
                    f"Wrote {len(all_stocks)} items to stock_prices.json"
                )
            except Exception as e:
                spider.logger.error(f"Failed to write stock_prices.json: {e}")
        else:
            spider.logger.warning("No stock items to write")
