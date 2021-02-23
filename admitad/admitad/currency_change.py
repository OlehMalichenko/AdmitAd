import csv
from pprint import pprint


def convert_price_(row):
	rate_dict = {
			'gbp': 101.9824,
			'usd': 73.9378,
			'eur': 89.6052
	}

	try:
		currency = row['currency'].strip().lower()
		rate = rate_dict[currency]
	except:
		return row
	else:
		try:
			row['price'] = float(row['price']) * rate
		except:
			print(f'ER price: {row["price"]}')
			return row
		try:
			row['sale_price'] = float(row['sale_price']) * rate
		except:
			print(f'ER sale_price: {row["sale_price"]}')
			pass
		row['currency'] = 'RUB'
		pprint(currency)
		return row


if __name__ == '__main__':
	currency_label = set()

	with open('files/asos_ADM_1.csv', 'r', encoding='utf-8') as f:
		reader = csv.DictReader(f)

		fielnames = list(reader.fieldnames) \
			# + ['currency']

		with open('files/asos_ADM_1_convert.csv', 'a', encoding='utf-8', newline='\n') as fc:
			writer = csv.DictWriter(fc, fieldnames=fielnames)
			writer.writeheader()

			for row in reader:
				# row['currency'] = 'RUB'
				# writer.writerow(row)
				writer.writerow(convert_price_(row))

		#         currency_label.add(row['currency'])
		#
		#
		# print(currency_label)
