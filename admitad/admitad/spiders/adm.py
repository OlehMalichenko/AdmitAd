import os

import scrapy

from ..api_zenscrape import _api_zenscrape, _get_url_from_api
from ..items import AdmitadItem
from ..s_intermodan import *
from ..utils_main import *


class AdmSpider(scrapy.Spider):
    name = 'adm'
    allowed_domains = []

    # PROXY ================================
    proxy_marker = False

    #              FALSE - without zenscrape
    #              TRUE - with proxy
    # ======================================

    def __init__(self, path=True, link=None, *args, **kwargs):
        super(AdmSpider, self).__init__(*args, **kwargs)
        if path:
            self.ad_urls = get_urls_from_csv(
                    file_path='C:\\Users\\advok\\PycharmProjects\\AdmitAd\\admitad\\admitad\\files\\intermodan.csv',
                    # check_file='C:\\Users\\advok\\PycharmProjects\\AdmitAd\\admitad\\admitad\\files\\aizel_start_urls.csv'
            )
            # self.ad_urls = get_urls_asos_tmp(
            #         file_path='C:\\Users\\advok\\PycharmProjects\\AdmitAd\\admitad\\admitad\\files\\rows_without_price.csv'
            # )
            # self.brands = get_check_brands()
        else:
            return

        self.used_file_path = 'C:\\Users\\advok\\PycharmProjects\\AdmitAd\\admitad\\admitad\\files\\intermodan_used_urls.csv'
        self.used_urls = []
        if not os.path.exists(self.used_file_path):
            open(self.used_file_path, 'a').close()
        with open(self.used_file_path, 'r', encoding='utf-8', newline='\n') as f:
            reader = csv.reader(f)
            for row in reader:
                self.used_urls.append(row[0])

    def start_requests(self):
        for url_tupl in self.ad_urls:
            # print(url_tupl)
            # brand = re.compile('[^a-zA-Zа-яА-ЯёЁ0-9]').sub('', url_tupl[3]).lower()
            if True:  # brand in self.brands:
                try:
                    if url_tupl[1] in self.used_urls:
                        continue

                    yield scrapy.Request(url=_api_zenscrape(url=url_tupl[0],
                                                            with_proxy=self.proxy_marker),
                                         callback=self.parse,
                                         dont_filter=True,
                                         meta={
                                                 'ref'          : url_tupl[1],
                                                 # 'category': url_tupl[3],
                                                 # 'brand': url_tupl[2],
                                                 'dont_redirect': True
                                         }, )
                    # break

                except:
                    print('----REQUEST----')
                    continue

    def parse(self, response, **kwargs):
        # print(response.url)
        # return
        response_url = _get_url_from_api(response_url=response.url,
                                         with_proxy=self.proxy_marker)

        # with open('intermodan_html.html', 'w', encoding='utf-8') as f:
        #     f.write(response.text)
        # print(response_url)
        # print(response.status)
        # return

        items_data_list = get_item_data(response)
        # pprint(items_data_list)
        # return

        if not items_data_list:
            print(f'----NOT ITEM {response_url}')
            # with open(f'{response_url}.html', 'w', encoding='utf-8') as f:
            #     f.write(response.text)
            return

        item_count = 0

        with open(self.used_file_path, 'a', encoding='utf-8', newline='\n') as f:
            writer = csv.writer(f)
            writer.writerow([response.meta['ref']])

        for item_data in items_data_list:
            item = AdmitadItem()
            item_count += 1

            for i_key, i_value in item_data.items():
                item[i_key] = i_value

            print(f'Item: {item_count}   {response_url}')

            yield item
