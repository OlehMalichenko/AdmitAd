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
    item['category'] = get_breadcrumbs(tree)

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

    for p in tree.xpath('//div[@class="about__menu--title"][contains(text(), "О товаре")]'
                        '/following-sibling::div[@class="about__menu--content"]/p'):
        try:
            tlt = p.xpath('./strong/text()')[0].strip()
            vl = p.xpath('text()')[0].strip()

            par = f'{tlt} {vl}'
            param_list.append(par)

            if 'цвет' in tlt.lower():
                color = vl

            if 'страна' in tlt.lower():
                country = vl
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
    size_list = tree.xpath('//div[@class="about__size--list"]'
                           '//a[@class="element__link"]/text()')
    return [t.strip().replace('\t', '').replace('\n', '')
            for t in size_list]


def get_description(tree):
    description_list = tree.xpath('//div[@itemprop="description"]/text()'
                                  '|//div[@itemprop="description"]//*/text()')
    if description_list:
        return ' '.join([t.strip() for t in description_list])
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
        href = tree.xpath('//div[@class="gallery__photo"]'
                          '//img/@src')[0]
        return f'https://www.keng.ru{href}'
    except:
        return ''


def get_site_name(tree):
    try:
        return tree.xpath('')[0]
    except:
        return 'Svmoscow.ru'


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
