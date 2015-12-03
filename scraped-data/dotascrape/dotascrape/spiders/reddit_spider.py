import scrapy

from dotascrape.items import DotaCommentItem

class RedditSpider(scrapy.Spider):
    name = "reddit"
    allowed_domains = ["reddit.com"]
    start_urls = [
       "http://www.reddit.com/r/dota2/"
    ]
    PAGE_LIMIT = 1
    page_count = 0

    def parse(self, response):
        yield scrapy.Request(response.url, callback=self.parse_follow_next_page)

    def parse_comments(self, response):
        #<div class="usertext-body may-blank-within md-container "> <-- space at the end?
        #   <div class="md">
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
        for commentlink in response.xpath("//a[contains(@class, 'comments') and contains(@class, 'may-blank')]/@href"):
            #("//a[@class="comments may-blank"]/@href"):
            #<a class="comments may-blank"/> <-- comment links
            url = response.urljoin(commentlink.extract())
            yield scrapy.Request(url, callback=self.parse_comments)

        next_page = response.xpath("//a[contains(@rel, 'nofollow') and contains(@rel, 'next')]/@href")
        self.page_count += 1
        if (next_page and self.page_count < self.PAGE_LIMIT):
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse_follow_next_page)
            