import scrapy
# import cfscrape

from dotascrape.items import DotaCommentItem

USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36',
    'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:34.0) Gecko/20100101 Firefox/34.0',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
    'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53 (compatible; bingbot/2.0; http://www.bing.com/bingbot.htm)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; Media Center PC',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.112 Safari/535.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0',
    'Mozilla/5.0 (iPad; U; CPU OS 5_1 like Mac OS X) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B367 Safari/531.21.10 UCBrowser/3.4.3.532'
]

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36'

class NadotaSpider(scrapy.Spider):
    name = "nadota"
    allowed_domains = ["nadota.com"]
    #allowed_domains = ["googleusercontent.com"]

    start_urls = [
       "http://nadota.com/forumdisplay.php?29-DotA-Chat"
       #"https://webcache.googleusercontent.com/search?q=cache:5xGpTDffnQUJ:nadota.com/forumdisplay.php%3F29-DotA-Chat+&cd=1&hl=en&ct=clnk&gl=ca"
    ]

    PAGE_LIMIT = 100000
    page_count = 0
    #override parse_start_url of Spider class to deal with cloudflare cookie
    #https://mktums.github.io/article/dealing-with-cloudflare-in-scrapy.html
    #def parse_start_url(self, response):
    #    self.cookie = response.headers.get('Set-Cookie').split(';')[0]
    #    return super(Spider, self).parse_start_url(response)


    #def start_requests(self):
    #    cfscraper = cfscrape.create_scraper()
    #    filename = 'nadota.html'
    #    with open(filename, 'wb') as f:
    #        f.write(cfscraper.get("http://nadota.com/forumdisplay.php?29-DotA-Chat").content)
    #
    #    cf_requests = []
    #    for url in self.start_urls:
    #        token, agent = cfscrape.get_tokens(url, USER_AGENT)
    #        #token, agent = cfscrape.get_tokens(url)
    #        cf_requests.append(scrapy.Request(url=url, cookies={'__cfduid': token['__cfduid']}, headers={'User-Agent': agent}))
    #        print "useragent in cfrequest: " , agent
    #        print "token in cfrequest: ", token
    #    return cf_requests

    def parse(self, response):
            yield scrapy.Request(response.url, callback=self.parse_follow_next_page)

    def parse_comments(self, response):
        # regular post:
        #<div id="post_message_#####">
        #   <blockquote class ="postcontent restore "> comment text </blockquote>
        # ...
        # post with quotes/images:
        # ...
        for comment in response.xpath(
            "//div[contains(@id, 'post_message')]/blockquote[contains(@class, 'postcontent')]"):
            #extract comment info
            item = DotaCommentItem()
            item['link'] = response.url
            item['desc'] = comment.xpath('text()').extract()
            item['user'] = comment.xpath("../../../../..//a[contains(@class, 'username')]/strong/text()").extract()
            # some users have font colours
            if (not item['user']):
                item['user'] = comment.xpath("../../../../..//a[contains(@class, 'username')]/strong/font/text()").extract()
            yield item
        
        next_comment_page = response.xpath("//a[contains(@rel, 'next') and contains(@title, 'Next Page')]/@href")
        if (next_comment_page):
            # go to next page of current thread and parse comments
            url = response.urljoin(next_comment_page[0].extract())
            yield scrapy.Request(url, self.parse_comments)

    def parse_follow_next_page(self, response):
        # grab all thread links
        for commentlink in response.xpath("//a[contains(@id, 'thread_title')]/@href"):
            # <a class="title threadtitle_unread"/>  OR <a class="title"/> <-- comment links
            url = response.urljoin(commentlink.extract())
            yield scrapy.Request(url, callback=self.parse_comments)

        next_page = response.xpath("//a[contains(@rel, 'next') and contains(@title, 'Next Page')]/@href")
        self.page_count += 1
        if (next_page and self.page_count < self.PAGE_LIMIT):
            # go to next page if exists and page limit not hit
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse_follow_next_page)
            