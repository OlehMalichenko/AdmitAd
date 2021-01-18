import scrapy
from ..utils_main import *
from ..utils_elyts import *
from ..utils_vipavenue import *
from ..urls import *
from ..items import AdmitadItem

class AdmSpider(scrapy.Spider):
    name = 'adm'
    allowed_domains = []

    def __init__(self, link=None, *args, **kwargs):
        super(AdmSpider, self).__init__(*args, **kwargs)
        self.url = link

    # ==========DISPATCH METHODS============= #
    def method_selection_using_(self, test_url):
        if 'elyts.ru' in test_url:
            return self.parse_elyst

        if 'vipavenue.ru' in test_url:
            return self.parse_vipavenue

    def start_requests(self):
        if self.url is None:
            self.url = get_start_url()

        yield scrapy.Request(url=self.url,
                             callback=self.parse)

    def parse(self, response, **kwargs):
        urls = get_urls_from_(response.body)

        # !!!!!!!!!!!!!!TEST
        # with open('vipavenue_links.csv', 'a', encoding='utf-8', newline='\n') as file:
        #     writer = csv.writer(file)
        #     for elem in urls:
        #         writer.writerow(elem)

        # !!!!!!!!!!!!!!TEST
        # count = 0

        parse_method = self.method_selection_using_(get_test_url_from_(urls))
        # print(parse_method.__name__)

        for pr_url in urls:

            # !!!!!!!!!!!!!!TEST
            # count += 1

            try:

                yield scrapy.Request(url=pr_url[0],
                                     callback=parse_method,
                                     dont_filter=True,
                                     meta={
                                             'ref': pr_url[1]
                                     })

                # !!!!!!!!!!!!!!TEST
                # if count == 20:
                #     break

            except:
                continue

    def parse_vipavenue(self, response, **kwargs):
        items_data_list = vipavenue_collector(response)
        item_count = 0

        for item_data in items_data_list:
            item = AdmitadItem()
            item_count += 1

            for i_key, i_value in item_data.items():
                item[i_key] = i_value

            print(f'Item: {item_count}   {response.url}')

            yield item

    def parse_elyst(self, response, **kwargs):
        items_data_list = elyts_collector(response)
        item_count = 0

        for item_data in items_data_list:
            item = AdmitadItem()
            item_count += 1

            for i_key, i_value in item_data.items():
                item[i_key] = i_value

            print(f'Item: {item_count}   {response.url}')

            yield item
