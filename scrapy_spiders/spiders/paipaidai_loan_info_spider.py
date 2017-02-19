# -*- coding: utf-8 -*-
import logging
import re

from scrapy import Selector
from palmutil.logger_util import JarvisLogger
from crawler.items.paipaidai_items import PaipaidaiLoanInfo
from my_scrapy_redis.spiders import RedisSpider
from palmutil.time_util import get_current_timestamp_str


class PaipaidaiLoanInfoSpider(RedisSpider):
    name = 'paipaidai_loan_info'
    redis_key = 'paipaidai:loaninfo_urls'
    custom_settings = {
        'SCHEDULER': "scrapy.core.scheduler.Scheduler",
        'ITEM_PIPELINES': {
            'crawler.pipelines.paipaidai_pipeline.PaipaidaiBusinessPipeline': 400
        },
        'DOWNLOADER_MIDDLEWARES': {
            'crawler.middlewares.middlewares.RandomUserAgent': 1,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
            'crawler.middlewares.middlewares.ProxyMiddleware': 100
        },
        'RETRY_TIMES': 3,
        'DOWNLOAD_DELAY': 5,
        'RANDOMIZE_DOWNLOAD_DELAY': True
    }

    logging.getLogger('scrapy').setLevel(logging.DEBUG)
    logging.getLogger("scrapy").propagate = True

    def __init__(self):
        super().__init__()
        self.jarvis_logger = JarvisLogger(filename="paipaidai_loan_info_spider.log", level=logging.DEBUG)

    def parse(self, response):
        try:
            html = response.text
            selector = Selector(text=html)
            loaninfo = PaipaidaiLoanInfo()
            loaninfo['user_name'] = selector.xpath(
                '/html/body/div[3]/div[2]/div[1]/div[1]/div[1]/a[3]/text()').extract_first()
            loaninfo['successful_times'] = int(re.search(r'>(.*?)次成功', html).group(1)) if re.search(r'>(.*?)次成功',
                                                                                                    html) else -1
            loaninfo['failed_times'] = int(re.search(r'｜(.*?)次流标', html).group(1)) if re.search(r'>(.*?)次成功',
                                                                                                html) else -1
            loaninfo['credit_rank'] = re.search(r'creditRating(.*?)">', html).group(1).strip()
            loaninfo['crawl_date'] = get_current_timestamp_str("Asia/Shanghai")
            yield loaninfo
        except Exception as e:
            self.jarvis_logger.exception(e=e)
