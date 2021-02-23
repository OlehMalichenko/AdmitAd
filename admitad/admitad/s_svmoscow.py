import re

from lxml import html


def get_item_data(response):
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
    # Parameters
    # Country made
    # color tmp
    item['description'], item['parameters'], item['country'], color = get_params(tree)

    # Brand
    item['brand'] = get_brand(tree)

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


def get_brand(tree):
    brand_list = tree.xpath('//h1[@itemprop="brand"]/a/text()')

    if brand_list:
        return str(brand_list[0]).strip()
    else:
        return ''


def get_params(tree):
    descr = ''
    params = ''
    country = ''
    color = ''

    d = tree.xpath('//div[@class="detail-page-tabs"]'
                   '/div[@class="detail-page-tab detail-page-tab-description active"]')
    if len(d) > 1:
        descr = ''.join(d[0].xpath('.//p/text()'))
        params_list = d[1].xpath('.//p/text()')
    else:
        params_list = d[0].xpath('.//p/text()')

    reg1 = re.compile(r'\w+:')
    reg2 = re.compile(r'[Цц]вет:(.+)')
    reg3 = re.compile(r'[0-9]')

    for p in params_list:
        if not reg1.findall(p):
            if not reg3.findall(p):
                country = p.strip()

        else:
            try:
                color = reg2.findall(p)[0].strip()
            except:
                continue

    descr = re.sub("^\s+|\n|\r|\s+$", '', descr)

    params_list = [re.sub("^\s+|\n|\r|\s+$", '', pr) for pr in params_list]
    params = ' / '.join(params_list)

    return descr, params, country, color


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
    return tree.xpath('//div[@class="select-size"]/a/text()')


def get_description(tree):
    description_list = tree.xpath('//div[@id="goods_description"]/text()')
    if description_list:
        return str(description_list[0]).strip()
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
    try:
        price = _create_float_price(tree.xpath('//meta[@itemprop="price"]/@content')[0])
    except:
        pass

    try:
        reg = re.compile(r'([0-9\s]*)\s*руб')
        old_price_text = tree.xpath('//span[@class="discount-price"]/text()')[0]
        old_price = _create_float_price(reg.findall(old_price_text)[0])
    except:
        pass

    return price, old_price


def get_product_name(tree):
    name = tree.xpath('//meta[@itemprop="name"]/@content')
    if name:
        return str(name[0]).strip()
    else:
        return 'No name'


def get_product_sku(tree):
    reg = re.compile('{\s*"id":')
    reg2 = re.compile('"id":\s*"(\w+)"')
    script = tree.xpath(f"//script[contains(text(), 'gtag')]/text()")
    for scr in script:
        if reg.findall(scr):
            try:
                return reg2.findall(scr)[0]
            except:
                continue
    return ''


def get_product_image(tree):
    try:
        return tree.xpath('//img[@type="image"]/@src')[0]
    except:
        return ''


def get_site_name(tree):
    try:
        return tree.xpath('')[0]
    except:
        return 'Svmoscow.ru'


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
