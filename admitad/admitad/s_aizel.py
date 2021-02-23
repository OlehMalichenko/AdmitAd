import unicodedata

import demjson
from lxml import html


def get_item_data(response):
	result_aft_size = []
	result_aft_color = []
	item = dict()

	try:
		tree = html.fromstring(response.body)
	except:
		print('----------NOT TREE----------')
		with open('aizel.html', 'w') as f:
			f.write(response.body)
		return []

	script = get_script_data(tree)

	# Ref_link
	item['ref'] = response.meta['ref']

	# Site-name
	item['site_name'] = get_site_name(tree)

	# Breadcrumbs
	item['category'] = get_breadcrumbs(script)

	# Name
	item['name'] = get_product_name(script)

	# SKU
	item['sku'] = get_product_sku(script)

	# Image link
	item['img'] = get_product_image(script)

	# Prices
	item['price'], item['old_price'] = get_price(script)

	# Description
	item['description'] = get_description(script)

	# Country made
	item['country'] = get_country_made(tree)

	# Brand
	item['brand'] = get_brand(script)

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

	return result_aft_color


def get_script_data(tree):
	try:
		script_text = tree.xpath('//script[contains(text(), "var digitalData=")]/text()')[0]
		s = script_text.find('{')
		e = script_text.rfind('}') + 1
		script_text = script_text[s: e]
		return demjson.decode(script_text)
	except:
		return ''


def get_brand(script):
	try:
		return script['product']['manufacturer']
	except:
		return ''


def get_params(tree):
	result = []
	detail_list = tree.xpath('//div[@class="m-accordion"]')
	if detail_list:
		for div in detail_list:
			try:
				if 'детали' in div.xpath('./button[contains(@class, "m-accordion__heading")]/text()')[0].lower():
					for t in div.xpath('.//li/text()'):
						if not t.strip():
							continue
						result.append(unicodedata.normalize('NFKD', t).strip())
			except:
				continue
	return result


def get_country_made(tree):
	detail_list = tree.xpath('//div[@class="m-accordion"]')
	if detail_list:
		for div in detail_list:
			try:
				if 'детали' in div.xpath('./button[contains(@class, "m-accordion__heading")]/text()')[0].lower():
					for t in div.xpath('.//li/text()'):
						if 'страна' in t.lower():
							return unicodedata.normalize('NFKD', t)

			except:
				continue
	return ''


def get_color(tree):
	color_list = tree.xpath('//div[@class="a-text -muted h-marginBottomSM"]'
	                        '/span/text()')
	if color_list:
		return color_list
	else:
		return []


def get_size(tree):
	result = []
	sizes_list = tree.xpath('//option[@class="ss-sizeSelect"]')

	for size in sizes_list:
		try:
			if 'нет' in size.get('data-description'):
				continue
			result.append(size.get('data-size'))
		except:
			continue
	return result


def get_description(script):
	try:
		return script['product']['description']
	except:
		return ''


def get_price(script):
	try:
		return script['product']['unitSalePrice'], script['product']['unitPrice']
	except:
		return 0, 0


def get_product_name(script):
	try:
		return script['product']['name']
	except:
		return ''


def get_product_sku(script):
	try:
		return script['product']['skuCode']
	except:
		return ''


def get_product_image(script):
	try:
		return script['product']['imageUrl']
	except:
		return ''


def get_site_name(tree):
	site_name = tree.xpath('//meta[@property="og:site_name"]/@content')
	if site_name:
		return site_name[0]
	else:
		return ''


def get_breadcrumbs(script):
	try:
		return '/'.join(script['product']['category'])
	except:
		return ''
