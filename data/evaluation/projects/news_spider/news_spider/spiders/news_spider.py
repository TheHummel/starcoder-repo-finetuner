from pathlib import Path
import scrapy
from scrapy.loader import ItemLoader
from news_spider.items import NewsSpiderItem


class NewsSpider(scrapy.Spider):
    name = "news_spider"

    def start_requests(self):
        urls = [
            "https://www.nzz.ch",
            "https://www.welt.de",
            "https://www.bild.de",  # Added from your logs
        ]
        for url in urls:
            site = url.split(".")[-2]  # e.g., 'nzz', 'welt', 'bild'
            yield scrapy.Request(url=url, callback=self.parse, meta={"site": site})

    def parse(self, response):
        site = response.meta["site"]
        articles = response.css("article") or response.css(
            ".article"
        )  # Fallback selector
        if not articles:
            self.logger.warning(f"No articles found on {response.url}")
            return

        for article in articles:
            loader = ItemLoader(item=NewsSpiderItem(), selector=article)
            loader.add_css("headline", "h2::text, h3::text, .headline::text")
            loader.add_value(
                "url", response.urljoin(article.css("a::attr(href)").get())
            )
            loader.add_value("topic", self.guess_topic(article))
            loader.add_value("site", site)  # Now valid
            yield loader.load_item()

    def guess_topic(self, article):
        text = article.css("::text").getall()
        text_str = "".join(text).lower()
        if any(k in text_str for k in ["economy", "business", "markt"]):
            return "economy"
        elif any(k in text_str for k in ["politik", "politics"]):
            return "politics"
        return "general"

    def closed(self, reason):
        self.logger.info(f"News spider closed: {reason}")
