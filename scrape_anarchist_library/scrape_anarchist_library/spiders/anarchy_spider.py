import scrapy

class AnarchySpider(scrapy.Spider):
    name = 'anarchy'

    def start_requests(self):
        url = 'http://theanarchistlibrary.org/listing?sort=title_asc&rows=500'
        pages = range(1,8)
        # German version
        # url = 'http://anarchistischebibliothek.org/listing?sort=title_asc&rows=500'
        # pages = range(1,3)
        for page in pages:
            self.log('%s&page=%s' % (url, page))
            yield scrapy.Request(url='%s&page=%s' % (url, page), callback=self.request_texts)

    def request_texts(self, response):
        for href in response.css('a.list-group-item::attr(href)'):
            full_link = '%s.muse' % href.extract()
            yield scrapy.Request(url=full_link, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-1]
        filename = '%s.txt' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
