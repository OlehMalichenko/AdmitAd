import re

import demjson
from lxml import html


def get_item_data(response):
    result_aft_size = []
    result_aft_color = []
    item = dict()

    tree = html.fromstring(response.text)

    script = get_script_data(tree)
    # pprint(script)
    # return script_text
    # Ref_link
    item['ref'] = response.meta['ref']

    # Site-name
    item['site_name'] = get_site_name(tree)

    # Breadcrumbs
    item['category'] = response.meta['category']

    # Name
    item['name'] = get_product_name(script)

    # Brand
    item['brand'] = get_brand(script)

    # SKU
    item['sku'] = get_product_sku(script)

    # Image link
    item['img'] = get_product_image(script)

    # Prices
    item['price'], item['sale_price'] = get_price(tree)

    if not item['name'] and not item['brand'] and not item['sku'] and not item['price']:
        return []

    item['currency'] = get_currency(script)

    # Description
    # Parameters
    # Country made
    # color tmp
    item['description'] = get_description(script)
    item['parameters'], item['country'] = get_params(tree)
    color = get_color(script)

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
        script_text = tree.xpath('//script[@id="structured-data"]/text()')[0]
        return demjson.decode(script_text)
    except:
        return ''


def get_brand(script):
    try:
        return script['brand']['name']
    except:
        return ''


def get_params(tree):
    params = ''
    country = ''

    params_list = tree.xpath('//div[@class="product-description"]'
                             '/ul'
                             '/li/text()')

    if params_list:
        params_list = [t.strip().replace('\n', '') for t in params_list]
        params = ' / '.join(params_list)

    return params, country


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


def get_color(script):
    try:
        return script['color']
    except:
        return ''


def get_size(tree):
    try:
        sizes_text = tree.xpath('//select[@id="main-size-select-0"]'
                                '/option[not(contains(@disabled, .))]/text()')

        return [t.strip()
                for t in sizes_text
                if 'выберит' not in t and 'Недоступн' not in t]
    except:
        return []


def get_description(script):
    try:
        return script['description']
    except:
        return ''


def _create_float_price(price):
    try:
        return float(''.join(re.compile(r'[0-9,]').findall(price)).replace(',', '.'))  # <<-- CHECK REG for symbols
    except:
        return 0.0


def get_price(tree):
    price = 0.0
    sale_price = 0.0

    current_price = tree.xpath(
            '//span[contains(@class, "current-price")][@data-id="current-price"]/text()')
    if current_price:
        cp = _create_float_price(current_price[0])
        prev_price = tree.xpath('//span[@class="product-prev-price"]/text()')
        if prev_price:
            price = _create_float_price(prev_price[0])
            sale_price = cp
        else:
            price = cp

    return price, sale_price


def get_currency(script):
    try:
        return script['offers']['priceCurrency'].strip()
    except:
        return ''


def get_product_name(script):
    try:
        return script['name'].strip()
    except:
        return ''


def get_product_sku(script):
    try:
        return f'Asos{script["sku"]}'
    except:
        return ''


def get_product_image(script):
    try:
        return script['image']
    except:
        return ''


def get_site_name(tree):
    try:
        return tree.xpath('')[0]
    except:
        return 'Asos.com'


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
