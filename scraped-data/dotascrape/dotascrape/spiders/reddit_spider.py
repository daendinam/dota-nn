import scrapy
import time

from dotascrape.items import DotaCommentItem

class RedditSpider(scrapy.Spider):
    name = "reddit"
    allowed_domains = ["reddit.com"]
    start_urls = [
       "https://www.reddit.com/r/DotA2/top/?sort=top&t=all"
    ]
    PAGE_LIMIT = 100000
    page_count = 0

    def parse(self, response):
        # old spider searched from top of subreddit, but this has limit of 1000 threads
        # - now uses search in time intervals to get full history
        start = 1293840000 #2011/1/1
        finish = start + 86400 #number of seconds in a day
        while finish <= (int(time.time()) + 86400):
            url = "http://reddit.com/r/DotA2/search?q=(and+subreddit:'dota2'+timestamp:" \
                   + str(start) + ".." + str(finish) + ")&syntax=cloudsearch&sort=new"
            start = finish
            finish = start + 86400
            yield scrapy.Request(url, callback=self.parse_follow_next_page)

    def parse_comments(self, response):
        #<div class="usertext-body may-blank-within md-container ">
        #       <p> comment body </p>
        # ...
        for comment in response.xpath("//div[contains(@class, 'usertext-body')" \
                                      "and contains(@class, 'may-blank-within')" \
                                      "and contains(@class, 'md-container')]/div[@class='md']/p"):
            # extract comment text
            item = DotaCommentItem()
            item['link'] = response.url
            item['desc'] = comment.xpath('text()').extract()
            # username html: comment.super^4.<p class="tagline"> <a class="author">username</a>..
            item['user'] = comment.xpath("../../../../p[contains(@class, 'tagline')]/a[contains(@class, 'author')]/text()").extract()
            # item['user'] = comment.xpath("./ancestor::p[contains(@class, 'tagline')[a[contains(@class, 'author')]]][1]/text()")
	    yield item

    def parse_follow_next_page(self, response):
        for commentlink in response.xpath("//a[contains(@class, 'search-comments') and contains(@class, 'may-blank')]/@href"):
            #("//a[@class="search-comments may-blank"]/@href"):
            #<a class="search-comments may-blank"/> <-- comment links
            url = response.urljoin(commentlink.extract())
            yield scrapy.Request(url, callback=self.parse_comments)

        next_page = response.xpath("//a[contains(@rel, 'nofollow') and contains(@rel, 'next')]/@href")
        self.page_count += 1
        if (next_page and self.page_count < self.PAGE_LIMIT):
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse_follow_next_page)
            