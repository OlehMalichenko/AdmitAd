import csv
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


def get_test_url_from_(urls):
    while True:
        try:
            test_url = choice(urls)[0]
            if test_url:
                return test_url
        except:
            continue
