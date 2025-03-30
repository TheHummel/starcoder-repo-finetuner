import scrapy
from scrapy_splash import SplashRequest
from stock_spider.items import StockItem


class StockSpider(scrapy.Spider):
    name = "stock_spider"
    allowed_domains = ["finanzen.ch", "localhost"]

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_DELAY": 2.0,
        "SPLASH_URL": "http://localhost:8050",
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy_splash.SplashCookiesMiddleware": 723,
            "scrapy_splash.SplashMiddleware": 725,
            "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810,
        },
        "SPIDER_MIDDLEWARES": {
            "scrapy_splash.SplashDeduplicateArgsMiddleware": 100,
        },
        "FEEDS": {
            "stock_prices.json": {
                "format": "json",
                "encoding": "utf8",
                "indent": 2,
                "overwrite": True,
            },
        },
    }

    isin_to_url = {
        "CH0012005267": "novartis-aktie",
        "CH0244767585": "ubs-aktie",
        "CH0038863350": "nestle-aktie",
    }

    def start_requests(self):
        base_url = "https://www.finanzen.ch/aktien/"
        script = """
        function main(splash)
            splash.private_mode_enabled = false
            splash:set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')
            splash:go(splash.args.url)
            splash:wait(5.0)
            return splash:html()
        end
        """
        for isin, slug in self.isin_to_url.items():
            url = f"{base_url}{slug}"
            self.logger.info(f"Requesting {url} for ISIN {isin}")
            yield SplashRequest(
                url=url,
                callback=self.parse,
                meta={"isin": isin},
                endpoint="execute",
                args={"lua_source": script},
            )

    def parse(self, response):
        isin = response.meta["isin"]
        if response.status != 200:
            self.logger.error(f"Failed to load {response.url}: {response.status}")
            return

        item = StockItem()
        item["isin"] = isin

        # extract name (full text, preserving spaces)
        name = response.css("span.snapshot__label::text").get()
        item["name"] = name.strip() if name else None

        # extract other fields (first match)
        price = response.css('div[data-field="Mid"] span.push-data::text').get()
        item["price"] = price.strip() if price else None

        change_abs = response.css(
            'div[data-field="changeabs"] span.push-data::text'
        ).get()
        item["change_absolute"] = change_abs.strip() if change_abs else None

        change_pct = response.css(
            'div[data-field="changeper"] span.push-data::text'
        ).get()
        item["change_percent"] = change_pct.strip() if change_pct else None

        self.logger.info(f"Scraped item for ISIN {isin}: {item}")
        if not item.get("price"):
            self.logger.warning(
                f"No price found for {response.url} - check page rendering"
            )
        yield item
