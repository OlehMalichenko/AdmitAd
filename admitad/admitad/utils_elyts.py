import csv
from random import choice
from urllib.parse import unquote
import re
from lxml import html


def elyts_collector(response):
    result_aft_size = []
    result_aft_color = []
    item = dict()

    tree = html.fromstring(response.text)

    # Ref_link
    item['ref'] = response.meta['ref']

    # Site-name
    item['site_name'] = get_site_name(tree)

    # Breadcrumbs
    item['category'] = get_breadcrumbs(tree)

    # Name
    item['name'] = get_product_name(tree)

    # SKU
    item['sku'] = get_product_sku(tree)

    # Image link
    item['img'] = get_product_image(tree)

    # Prices
    item['price'], item['old_price'] = get_price(tree)

    # Description
    item['description'] = get_description(tree)

    # Country made
    item['country'] = get_country_made(tree)

    # Brand
    item['brand'] = get_brand(tree)

    # Parameters
    item['parameters'] = get_params(tree)

    # Items. Sizes and Colors variants
    # Size
    size_list = get_size(tree)
    if size_list:
        for size in size_list:
            item_size_variant = item.copy()
            item_size_variant['size'] = str(size).strip()
            result_aft_size.append(item_size_variant)
    else:
        result_aft_size.append(item)

    # Color
    color_list = get_color(tree)
    if color_list:
        for item_size_variant in result_aft_size:
            for color in color_list:
                item_color_variant = item_size_variant.copy()
                item_color_variant['color'] = str(color).strip()
                result_aft_color.append(item_color_variant)
    else:
        result_aft_color = result_aft_size

    return result_aft_color


def get_brand(tree):
    brand_list = tree.xpath('//div[@class="b-product__title"]'
                            '/a/@title'
                            '|'
                            '//div[@class="b-product__title"]'
                            '/span[@itemprop="brand"]/text()')

    if brand_list:
        return str(brand_list[0]).strip()
    else:
        return ''


def get_params(tree):
    params = []
    detail_list = tree.xpath('//div[@class="params-pane tab-pane-content"]'
                             '/div')
    if detail_list:
        for div in detail_list:
            first_div = div.xpath('./div[1]/text()')
            second_div = div.xpath('./div[2]/text()')
            second_div_1 = div.xpath('./div[2]/a/text()')

            if first_div:
                tmp = ''
                if second_div:
                    tmp = f'{str(first_div[0]).replace(":", "").strip()} : {str(second_div[0]).strip()}'
                if second_div_1:
                    tmp = f'{str(first_div[0]).replace(":", "").strip()} : {str(second_div_1[0]).strip()}'

                if tmp:
                    params.append(tmp)
    if params:
        return ', '.join(params)
    else:
        return ''


def get_country_made(tree):
    country = ''
    detail_list = tree.xpath('//div[@class="params-pane tab-pane-content"]'
                             '/div')
    if detail_list:
        for div in detail_list:
            first_div = div.xpath('./div[1]/text()')
            second_div = div.xpath('./div[2]/text()')
            second_div_1 = div.xpath('./div[2]/a/text()')

            if first_div:
                if 'страна' in str(first_div[0]).replace(' ', '').lower():

                    if second_div:
                        country = str(second_div[0]).lower().strip()
                    if second_div_1:
                        country = str(second_div_1[0]).lower().strip()

    if len(country) <= 3:
        country = country.upper()
    else:
        country = country.title()

    return country


def get_color(tree):
    color_list = tree.xpath('//div[@class="ajaxColorList b-product__color"]'
                            '/span/text()')
    if color_list:
        return color_list
    else:
        return []


def get_size(tree):
    sizes_list = tree.xpath('//div[@id="product-card-select"]'
                            '//div[@class="b-size-select__pane"]'
                            '//option[@data-reserv]/text()')
    if sizes_list:
        return sizes_list
    else:
        return []


def get_description(tree):
    description_list = tree.xpath('//div[@id="goods_description"]/text()')
    if description_list:
        return str(description_list[0]).strip()
    else:
        return ''


def get_price(tree):
    price = ''
    old_price = ''

    price_list = tree.xpath('//div[@itemprop="offers"]'
                            '/meta[@itemprop="price"]/@content')
    old_price_list = tree.xpath('//div[@itemprop="offers"]'
                                '//div[@class="price-item rub-symbol "]'
                                '/del/text()')
    if price_list:
        price = price_list[0]

    if old_price_list:
        old_price_re = re.compile('[0-9]').findall(str(old_price_list[0]))
        if old_price_re:
            old_price = int(''.join(old_price_re))

    return price, old_price


def get_product_name(tree):
    name = tree.xpath('//nav[@class="col-12 breadcrumbs"]'
                      '//li'
                      '/h1[@itemprop="name"]/text()')
    if name:
        return str(name[0]).strip()
    else:
        return 'No name'


def get_product_sku(tree):
    sku = tree.xpath('//div[@class="col-md-6 col-lg-4 b-product"]'
                     '/meta[@itemprop="sku"]/@content')
    if sku:
        return str(sku[0]).strip()
    else:
        return ''


def get_product_image(tree):
    img = tree.xpath('//div[@class="col-md-6 col-lg-4 b-product"]'
                     '/meta[@itemprop="image"]/@content')
    if img:
        return str(img[0]).strip()
    else:
        return ''


def get_site_name(tree):
    site_name = tree.xpath('//meta[@property="og:site_name"]/@content')
    if site_name:
        return site_name[0]
    else:
        return ''


def get_breadcrumbs(tree):
    b_crumbs = tree.xpath('//nav[@class="col-12 breadcrumbs"]'
                          '//li'
                          '/a/text()')
    try:
        gender = str(b_crumbs[1]).lower().strip()
    except:
        return ''

    if 'женщ' not in gender and 'муж' not in gender:
        gender = 'notGender'

    if len(b_crumbs) > 4:
        return '/'.join([gender.title(), b_crumbs[3], b_crumbs[4]])
    elif len(b_crumbs) == 4:
        return '/'.join([gender.title(), b_crumbs[3], b_crumbs[3]])
    elif len(b_crumbs) == 3:
        return '/'.join([gender.title(), b_crumbs[2], b_crumbs[2]])
