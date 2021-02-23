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
    item['description'] = get_description(tree)

    # Country made
    item['country'] = get_country_made(tree)

    # Brand
    item['brand'] = get_brand(tree)

    # Parameters
    item['parameters'] = get_params(tree)

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
    color_list = get_color(tree)
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

    # pprint(result_aft_color)
    return result_aft_color


def get_site_name(tree):
    site_name = tree.xpath('//meta[@property="og:site_name"]/@content')
    if site_name:
        return site_name[0]
    else:
        return ''


def get_breadcrumbs(tree):
    b_crumbs = tree.xpath('//ol[@class="breadcrumb js-breadcrumb"]'
                          '//li'
                          '/a/text()')
    try:
        gender = str(b_crumbs[1]).lower().strip()
    except:
        return ''

    if 'женс' not in gender and 'муж' not in gender:
        gender = 'notGender'

    if len(b_crumbs) > 4:
        return '/'.join([gender.title(), b_crumbs[3], b_crumbs[4]])
    elif len(b_crumbs) == 4:
        return '/'.join([gender.title(), b_crumbs[3], b_crumbs[3]])
    elif len(b_crumbs) == 3:
        return '/'.join([gender.title(), b_crumbs[2], b_crumbs[2]])


def get_product_name(tree):
    # name = tree.xpath('//h1[@class="product__title"]/text()')
    name = tree.xpath('//div[@id][@data-name][@data-fullimg][@data-id][@data-ecommercecategory]/@data-name')
    if name:
        return str(name[0]).strip()
    else:
        return 'No name'


def get_product_sku(tree):
    sku = tree.xpath('//div[@id][@data-name][@data-fullimg][@data-id][@data-ecommercecategory]/@data-id')
    if sku:
        return str(sku[0]).strip()
    else:
        return ''


def get_product_image(tree):
    img = tree.xpath('//div[@id][@data-name][@data-fullimg][@data-id][@data-ecommercecategory]/@data-fullimg')
    if img:
        return str(img[0]).strip()
    else:
        return ''


def get_price(tree):
    price = ''
    old_price = ''

    price_list = tree.xpath('//div[@id][@data-name][@data-fullimg][@data-id][@data-ecommercecategory]'
                            '/@data-ecommerceprice')
    old_price_list = tree.xpath('//del[@class="old-price js-catalog-detail-price-old"]/text()')
    if price_list:
        price = price_list[0]

    if old_price_list:
        old_price_re = re.compile('[0-9]').findall(str(old_price_list[0]))
        if old_price_re:
            old_price = int(''.join(old_price_re))

    return price, old_price


def get_brand(tree):
    brand_list = tree.xpath('//div[@id][@data-name][@data-fullimg][@data-id][@data-ecommercecategory]'
                            '/@data-ecommercebrand')

    if brand_list:
        return str(brand_list[0]).strip()
    else:
        return ''


def get_description(tree):
    description_list = tree.xpath('//div[@class="accordion-info-item-value js-accordion-item-value"]'
                                  '/div[@class="product-desc mb13"]'
                                  '/p/text()')
    if description_list:
        # return str(description_list[0]).strip()
        return ' '.join(description_list)
    else:
        return ''


def get_country_made(tree):
    country = ''
    detail_list = tree.xpath('//div[@class="accordion-info-item-value js-accordion-item-value"]'
                             '/ul[@class="product-desc-params"]'
                             '/li')
    if detail_list:
        for div in detail_list:
            first_span = div.xpath('./span[1]/span/text()')
            second_span = div.xpath('./span[2]/text()')
            second_div_1 = div.xpath('./span[2]/a/text()')

            if first_span:
                if 'страна' in str(first_span[0]).replace(' ', '').lower():

                    if second_span:
                        country = str(second_span[0]).lower().strip()
                    if second_div_1:
                        country = str(second_div_1[0]).lower().strip()

    if len(country) <= 3:
        country = country.upper()
    else:
        country = country.title()

    return country


def get_params(tree):
    params = []
    detail_list = tree.xpath('//div[@class="accordion-info-item-value js-accordion-item-value"]'
                             '/ul[@class="product-desc-params"]'
                             '/li')
    if detail_list:
        for div in detail_list:
            first_span = div.xpath('./span[1]/span/text()')
            second_span = div.xpath('./span[2]/text()')
            second_span_1 = div.xpath('./span[2]/a/text()')

            if first_span:
                tmp = ''
                if second_span:
                    tmp = f'{str(first_span[0]).replace(":", "").strip()} : {str(second_span[0]).strip()}'
                if second_span_1:
                    tmp = f'{str(first_span[0]).replace(":", "").strip()} : {str(second_span_1[0]).strip()}'

                if tmp:
                    params.append(tmp)
    if params:
        return ', '.join(params)
    else:
        return ''


def get_size(tree):
    sizes_list = tree.xpath('//div[contains(@id, "product")]/@data-ecommercevariant')
    return set(sizes_list)
    #
    # resul_size = []
    #
    # if sizes_list:
    #     for size in set(sizes_list):
    #         if 'нет' in size:
    #             continue
    #         resul_size.append(size.strip())
    #     # pprint(resul_size)
    #     return resul_size
    # else:
    #     return []


def get_color(tree):
    color = []
    detail_list = tree.xpath('//div[@class="accordion-info-item-value js-accordion-item-value"]'
                             '/ul[@class="product-desc-params"]'
                             '/li')
    if detail_list:
        for div in detail_list:
            first_span = div.xpath('./span[1]/span/text()')
            second_span = div.xpath('./span[2]/text()')
            second_div_1 = div.xpath('./span[2]/a/text()')

            if first_span:
                if 'цвет' in str(first_span[0]).replace(' ', '').lower():

                    if second_span:
                        color.append(str(second_span[0]).lower().strip())
                    if second_div_1:
                        color.append(str(second_div_1[0]).lower().strip())

    return color
