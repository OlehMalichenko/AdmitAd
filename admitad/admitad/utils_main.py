import csv
import re
from random import choice
from urllib.parse import unquote


def get_urls_from_(response_body):
	results = []
	check_list = []

	decoded_content = response_body.decode('utf-8')

	reader = csv.reader(decoded_content.splitlines(), delimiter=';')
	reader_list = list(reader)

	for row in reader_list:
		for ref_url in row:
			if 'https://ad.admitad.com' in str(ref_url):

				if ref_url in check_list:
					continue

				check_list.append(ref_url)

				try:
					prod_url = unquote(ref_url.split('&ulp=')[1])
					results.append([prod_url, unquote(ref_url)])
				except:
					continue

	return results


def get_urls_from_csv(file_path):
	results = []
	check_list = []

	with open(file_path, 'r', encoding='utf-8', ) as f:
		reader = csv.DictReader(f)
		for row in reader:
			for _, ur in row.items():
				if 'https://ad.admitad.com' in ur:
					if ur in check_list:
						continue

					check_list.append(ur)

					try:
						ur = unquote(ur)
						prod_url = ur.split('&ulp=')[1]
						results.append((prod_url, ur))
					except:
						continue
		# break
	return results


def get_urls_ref_category_from_file(file_path, check_file=None):
	results = []
	check_list = []

	if check_file is not None:
		with open(check_file, 'r', encoding='utf-8') as fc:
			reader = csv.reader(fc)
			for row in reader:
				try:
					check_list.append(row[0])
				except:
					continue

	with open(file_path, 'r', encoding='utf-8') as f:
		reader = csv.reader(f)
		# next(reader)
		for row in reader:
			if check_list:
				if row[0] in check_list:
					continue
			tpl = (
					row[0],  # prod_url
					row[1],  # ref
					# row[2], # brand
					# row[3]  # category
			)
			results.append(tpl)

	return results


def get_urls_asos_tmp(file_path):
	results = []
	check_list = []

	with open(file_path, 'r', encoding='utf-8') as f:
		reader = csv.DictReader(f)

		for row in reader:
			try:
				prod_url = row['ref'].split('&ulp=')[1]
			except:
				continue

			if prod_url in check_list:
				continue
			check_list.append(prod_url)

			tpl = (
					prod_url,  # prod_url
					row['ref'],  # ref
					row['brand'],  # brand
					row['category']  # category
			)
			results.append(tpl)

	return results


def get_test_url_from_(urls):
	while True:
		try:
			test_url = choice(urls)[0]
			if test_url:
				return test_url
		except:
			continue


def check_brands_list():
	results = set()
	reg = re.compile('[^a-zA-Zа-яА-ЯёЁ0-9]')
	with open('C:\\Users\\advok\\PycharmProjects\\AdmitAd\\admitad\\admitad\\files\\brand_list.csv', 'r',
	          encoding='utf-8') as f:
		reader = csv.DictReader(f)
		next(reader)

		for row in reader:
			if 'да' in row['we']:
				brand = reg.sub('', row['brand']).lower()
				results.add(brand)

	results = list(results)

	with open('C:\\Users\\advok\\PycharmProjects\\AdmitAd\\admitad\\admitad\\files\\brands_list_for_check.csv', 'a',
	          encoding='utf-8', newline='\n') as file:
		writer = csv.writer(file)

		for row in results:
			writer.writerow([row])

	return results


def get_check_brands():
	result = []
	with open('C:\\Users\\advok\\PycharmProjects\\AdmitAd\\admitad\\admitad\\files\\brands_list_for_check.csv', 'r',
	          encoding='utf-8', newline='\n') as file:
		reader = csv.reader(file)

		for row in reader:
			result.append(row[0])

	return result
