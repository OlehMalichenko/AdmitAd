import re

import demjson
from lxml import html


def get_item_data(response):
    result_aft_size = []
    result_aft_color = []
    item = dict()

    tree = html.fromstring(response.text)

    # script = get_script_data(tree)
    # pprint(script)
    # return script_text
    # Ref_link
    item['ref'] = response.meta['ref']

    # Site-name
    item['site_name'] = get_site_name(tree)

    # Breadcrumbs
    item['category'] = response.meta['category']

    # Name
    item['name'] = get_product_name(tree)

    # Brand
    item['brand'] = get_brand(tree)

    # SKU
    item['sku'] = get_product_sku(tree)

    # Image link
    item['img'] = get_product_image(tree)

    # Prices
    item['price'], item['sale_price'] = get_price(tree)

    if not item['name'] and not item['brand'] and not item['sku'] and not item['price']:
        return []

    # Description
    # Parameters
    # Country made
    # color tmp
    item['description'] = get_description(tree)
    item['parameters'] = get_params(tree)
    item['country'] = get_country_made(tree)

    # Items. Sizes and Colors variants
    # Size
    size_list = get_size(tree)
    product_type = ''
    if size_list:
        if len(size_list) > 1:
            product_type = 'variable'
        for size in size_list:
            item_size_variant = item.copy()
            item_size_variant['size'] = str(size).strip()
            item_size_variant['product_type'] = product_type
            result_aft_size.append(item_size_variant)
    else:
        result_aft_size.append(item)

    # Color
    color_list = get_color(tree)
    if color_list:
        if len(color_list) > 1:
            product_type = 'variable'
        for item_size_variant in result_aft_size:
            for col in color_list:
                item_color_variant = item_size_variant.copy()
                item_color_variant['color'] = str(col).strip()
                item_size_variant['product_type'] = product_type
                result_aft_color.append(item_color_variant)
    else:
        result_aft_color = result_aft_size

    return result_aft_color


def get_script_data(tree):
    try:
        script_text = tree.xpath('//script[@id="structured-data"]/text()')[0]
        return demjson.decode(script_text)
    except:
        return ''


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
        return ' '.join([t.strip().replace('\n', '').replace('\xa0', ' ')
                         for t in description_list
                         if t])
    else:
        return ''


def _create_float_price(price):
    try:
        return float(''.join(re.compile(r'[0-9\\.]').findall(price)))  # <<-- CHECK REG for symbols
    except:
        return 0.0


def get_price(tree):
    price = 0.0
    sale_price = 0.0

    price_list = tree.xpath('//div[@itemprop="offers"]'
                            '/meta[@itemprop="price"]/@content')
    old_price_list = tree.xpath('//div[@itemprop="offers"]'
                                '//div[@class="price-item rub-symbol "]'
                                '/del/text()')
    if price_list:
        p = _create_float_price(price_list[0])

        if old_price_list:
            price = _create_float_price(old_price_list[0])
            sale_price = p
        else:
            price = p

    return price, sale_price


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
        return f'Elits{str(sku[0]).strip()}'
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
