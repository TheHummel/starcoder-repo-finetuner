import scrapy
from scrapy.http import FormRequest
from scrapy.loader import ItemLoader
from price_spider.items import ProductItem


class PriceSpider(scrapy.Spider):
    name = "price_spider"
    start_urls = ["https://www.ebay.de", "https://www.zalando.de"]

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_DELAY": 3.0,
        "RETRY_TIMES": 5,
        "RETRY_HTTP_CODES": [403, 429],
    }

    def start_requests(self):
        site_configs = {
            "ebay": {"url": "https://www.ebay.de", "formdata": {"_nkw": "laptop"}},
            "zalando": {
                "url": "https://www.zalando.de",
                "formdata": {"q": "sneaker"},
            },  # TODO: fix with proxy
        }
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        for site, config in site_configs.items():
            self.logger.info(f"Starting request for {site} at {config['url']}")
            yield scrapy.Request(
                url=config["url"],
                callback=self.parse_form,
                meta={"site": site, "formdata": config["formdata"]},
                headers=headers,
                dont_filter=True,
            )

    def parse_form(self, response):
        site = response.meta["site"]
        formdata = response.meta["formdata"]
        self.logger.debug(f"Submitting form for {site}, status: {response.status}")
        if response.status != 200:
            self.logger.error(f"Form page failed for {site}: {response.status}")
            return
        yield FormRequest.from_response(
            response,
            formdata=formdata,
            callback=self.parse_results,
            meta={"site": site},
            headers={"Referer": response.url},
        )

    def parse_results(self, response):
        site = response.meta["site"]
        self.logger.debug(
            f"Parsing {response.url} for site: {site}, status: {response.status}"
        )

        if response.status != 200:
            self.logger.error(f"Failed to load {response.url}: {response.status}")
            return

        if site == "ebay":
            products = response.css(".s-item")
            if not products:
                self.logger.warning(f"No products found on {response.url}")
            for product in products:
                loader = ItemLoader(item=ProductItem(), selector=product)
                loader.add_css("name", ".s-item__title::text")
                loader.add_css("price", ".s-item__price::text")
                img_url = (
                    product.css("img.s-item__image-img::attr(src)").get()
                    or product.css("img::attr(src)").get()
                )
                loader.add_value("file_urls", [img_url] if img_url else [])
                loader.add_value("site", str(site))
                loader.add_value(
                    "product_url",
                    response.urljoin(product.css(".s-item__link::attr(href)").get()),
                )
                item = loader.load_item()
                self.logger.info(f"Yielding item for {site}: {item}")
                yield item

        elif site == "zalando":
            products = response.css(".z-grid-item, article, .cat_cardContainer__mVslz")
            if not products:
                self.logger.warning(f"No products found on {response.url}")
            for product in products:
                loader = ItemLoader(item=ProductItem(), selector=product)
                loader.add_css("name", "h3::text, .cat_headline__pXv-::text")
                loader.add_css("price", ".cat_price__pYvSL::text")
                img_url = product.css("img::attr(src)").get()
                loader.add_value("file_urls", [img_url] if img_url else [])
                loader.add_value("site", str(site))
                loader.add_value(
                    "product_url", response.urljoin(product.css("a::attr(href)").get())
                )
                item = loader.load_item()
                self.logger.info(f"Yielding item for {site}: {item}")
                yield item

    def spider_opened(self, spider):
        self.logger.info("Price spider opened!")
