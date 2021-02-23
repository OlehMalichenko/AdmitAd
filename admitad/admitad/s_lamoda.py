import re

import demjson
from lxml import html


def get_item_data(response):
    result_aft_size = []
    result_aft_color = []
    item = dict()

    tree = html.fromstring(response.text)

    script_text = get_script_data(tree)

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
    item['parameters'], item['country'], color = get_params(tree)

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
    if color:
        for item_size_variant in result_aft_size:
            for col in [color]:
                item_color_variant = item_size_variant.copy()
                item_color_variant['color'] = str(col).strip()
                result_aft_color.append(item_color_variant)
    else:
        result_aft_color = result_aft_size

    return result_aft_color


def get_script_data(tree):
    try:
        script_text = tree.xpath('//script[@data-module="statistics"]/text()')[0]
        start_ind = script_text.find('{')
        end_ind = script_text.rfind('};') + 1
        script_text = script_text[start_ind:end_ind]
        script_text = script_text.replace('=', ':')
        script_text = script_text.replace(';', ',')
        return script_text
    except:
        return ''


def get_brand(tree):
    brand_list = tree.xpath('//*[@class="product-title__brand-name"]/@title')

    if brand_list:
        return str(brand_list[0]).strip()
    else:
        return ''


def get_params(tree):
    params = ''
    country = ''
    color = ''

    d = tree.xpath('//div[@class="ii-product__attributes"]'
                   '/div[contains(@class, "ii-product__attribute")]')

    params_list = []

    for prm in d:
        try:
            label = prm.xpath('.//span[@class="ii-product__attribute-label"]/text()')[0].replace('\n', ' ')
            value = prm.xpath('.//span[@class="ii-product__attribute-value"]/text()')[0].replace('\n', ' ')

            label = ' '.join(label.split())
            value = ' '.join(value.split())

            if 'цвет' in label.lower():
                color = value

            if 'страна' in label.lower():
                country = value

            params_list.append(f'{label} {value}')
        except:
            continue

    if params_list:
        params = ' / '.join(params_list)

    return params, country, color


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
    try:
        sizes_text = tree.xpath('//div[contains(@class, "ii-product__buy")]/@data-fitting-sizes')[0].strip()
        sizes_list = demjson.decode(sizes_text)
        result = []
        for s in sizes_list:
            result.append(s['text'])
        return result
    except:
        return []


def get_description(tree):
    description_list = tree.xpath('//div[@class="ii-product__description-text"]'
                                  '/pre[@itemprop="description"]/text()')
    if description_list:
        return str(description_list[0]).strip().replace('\n', '').replace('\r', '')
    else:
        return ''


def _create_float_price(price):
    try:
        return float(''.join(re.compile(r'[0-9\\.]').findall(price)))  # <<-- CHECK REG for symbols
    except:
        return 0.0


def get_price(tree):
    price = 0.0
    old_price = 0.0

    price_list = tree.xpath('//span[@class="product-prices__price"]/text()')
    if not price_list:
        price_list = tree.xpath('//span[@class="_1xktn17sNuFwy45DZmZ5Oe"]/text()')
    if price_list:
        if len(price_list) > 1:
            price1 = _create_float_price(price_list[0])
            price2 = _create_float_price(price_list[1])
            if price1 >= price2:
                old_price = price1
                price = price2
            else:
                old_price = price2
                price = price1
        else:
            price = _create_float_price(price_list[0])

    if old_price:
        return old_price, price
    else:
        return price, 0.0


def get_product_name(tree):
    name = tree.xpath('//span[@class="product-title__model-name"]/text()')
    if name:
        return str(name[0]).strip()
    else:
        return 'No name'


def get_product_sku(tree):
    try:
        sku = tree.xpath('//div[@class="ii-product"]/@data-sku')[0]
        return f'Lamoda{sku}'
    except:
        return ''


def get_product_image(tree):
    try:
        href = tree.xpath('//div[@class="ii-product"]/@data-image')[0]
        return f'http:{href}'
    except:
        return ''


def get_site_name(tree):
    try:
        return tree.xpath('')[0]
    except:
        return 'Lamoda.ru'


def get_breadcrumbs(tree):
    reg = re.compile('"category":')
    reg2 = re.compile('"category":\s*"(.+)"')
    script = tree.xpath(f"//script[contains(text(), 'gtag')]/text()")
    for scr in script:
        if reg.findall(scr):
            try:
                return reg2.findall(scr)[0]
            except:
                continue
    return ''
