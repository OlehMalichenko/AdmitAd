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

    prod_info = get_product_data(tree)
    if not prod_info:
        return []

    item['ref'] = response.meta['ref']

    # Site-name
    item['site_name'] = get_site_name(tree)

    # Breadcrumbs
    item['category'] = prod_info['cat']

    # Name
    item['name'] = prod_info['name']

    # Brand
    item['brand'] = prod_info['brand']

    # SKU
    item['sku'] = prod_info['sku']

    # Image link
    item['img'] = get_product_image(tree)

    # Prices
    item['price'] = prod_info['price']
    item['sale_price'] = prod_info['sale_price']

    if not item['name'] and not item['brand'] and not item['sku'] and not item['price']:
        return []

    # Description
    # Parameters
    # Country made
    # color tmp
    item['description'] = get_description(tree)
    item['parameters'], item['country'], color = get_params(tree)

    if not item['price'] or not item['sku'] or not item['brand']:
        return []

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
    color_list = [color]
    if color_list:
        if len(color_list) > 1:
            product_type = 'variable'
        for item_size_variant in result_aft_size:
            for color in color_list:
                item_color_variant = item_size_variant.copy()
                item_color_variant['color'] = str(color).strip()
                item_color_variant['product_type'] = product_type
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
    brand_list = tree.xpath('//h1[@itemprop="name"]'
                            '/a/text()')

    if brand_list:
        return str(brand_list[0]).strip()
    else:
        return ''


def get_params(tree):
    country = ''
    color = ''
    param_list = []

    # d = tree.xpath('//div[@class="about__menu--title"][contains(text(), "О товаре")]'
    #                '/following-sibling::div[@class="about__menu--content"]/p')

    for p in tree.xpath('//button[contains(@data-analytics-name, "Информация об")]'
                        '/following-sibling::div[@class="panel-content"][1]'
                        '//p/text()'):
        p = re.sub(' +', ' ', p)
        param_list.append(p.strip().replace('\n', ' '))

        try:
            if 'цвет' in p.lower():
                try:
                    color = p.split(':')[1].strip()
                except:
                    pass

            if 'страна' in p.lower():
                try:
                    country = p.split(':')[1].strip()
                except:
                    pass
        except:
            continue

    if param_list:
        params = '/'.join(param_list)
    else:
        params = ''

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
    res = []
    sl = tree.xpath('//div[@class="sizes-block"]'
                    '/div[@class="size-value"]/@data-all-sizes')
    for s in sl:
        try:
            d = demjson.decode(s.strip())
            dl = [f'{k}:{v}' for k, v in d.items()]
            ds = ' - '.join(dl)
            res.append(ds)
        except:
            continue
    return res


def get_description(tree):
    descr_list = []

    # d = tree.xpath('//div[@class="about__menu--title"][contains(text(), "О товаре")]'
    #                '/following-sibling::div[@class="about__menu--content"]/p')

    for p in tree.xpath('//button[contains(@data-analytics-name, "Описание")]'
                        '/following-sibling::div[@class="panel-content"][1]'
                        '//p/text()'):
        p = re.sub(' +', ' ', p)
        descr_list.append(p.strip().replace('\n', ' '))

    if descr_list:
        descr = ' '.join(descr_list)
    else:
        descr = ''

    return descr


def _create_float_price(price):
    try:
        return float(''.join(re.compile(r'[0-9]').findall(price)))  # <<-- CHECK REG for symbols
    except:
        return 0.0


def get_price(tree):
    price = 0.0
    sale_price = 0.0

    try:
        price = _create_float_price(tree.xpath('//meta[@itemprop="price"]/@content')[0])
    except:
        pass

    try:
        old_price_text = tree.xpath('//span[@class="old-price-value"]'
                                    '/s/text()')[0]
        old_price = _create_float_price(old_price_text)
    except:
        old_price = 0.0

    if old_price > price:
        return old_price, price
    else:
        return price, sale_price


def get_product_name(tree):
    name = tree.xpath('//h1[@itemprop="name"]'
                      '/span/text()')
    if name:
        return str(name[0]).strip()
    else:
        return 'No name'


def get_product_sku(tree):
    reg2 = re.compile("prodid.*:\s*'(\w+)'")
    script = tree.xpath(f"//script[contains(text(), 'prodid')]/text()")
    for scr in script:
        if reg2.findall(scr):
            try:
                return f'Keng{reg2.findall(scr)[0]}'
            except:
                continue
    return ''


def get_product_image(tree):
    try:
        href = tree.xpath('//div[contains(@class, "swiper-wrapper")]'
                          '//img/@data-large')[0]
        return f'https://intermodann.ru{href}'
    except:
        return ''


def get_site_name(tree):
    try:
        return tree.xpath('')[0]
    except:
        return 'Intermodann.ru'


def get_breadcrumbs(tree):
    bc_list = tree.xpath('//div[@class="content__top--bc"]'
                         '/a[@class="bc__link"]/text()')
    if bc_list:
        bc_list = [t.strip()
                   for t in bc_list
                   if 'главная' not in t.lower() and 'каталог' not in t.lower()]
        return '/'.join(bc_list)
    else:
        return ''


def get_product_data(tree):
    result = dict()
    try:
        prod_info_cat_text = tree.xpath('//div[@id="product-info"]/@data-shop')[0].strip()
        prod_info_prc_text = tree.xpath('//div[@id="product-info"]/@data-vk')[0].strip()

        prod_info_cat = demjson.decode(prod_info_cat_text)
        prod_info_prc = demjson.decode(prod_info_prc_text)

        result['cat'] = prod_info_cat['category']
        result['sku'] = f"Intermodann{prod_info_cat['id']}"
        result['brand'] = prod_info_cat['brand']
        result['name'] = prod_info_cat['name']
        price = _create_float_price(str(prod_info_prc['products']['price']))
        try:
            old_price = _create_float_price(str(prod_info_prc['products']['price_old']))
        except:
            old_price = 0.0
        result['sale_price'] = price if old_price else 0.0
        result['price'] = price if not old_price else old_price
        result['currency'] = prod_info_cat.get('currency') if prod_info_cat.get('currency') is not None else ''

    except:
        return result

    return result
