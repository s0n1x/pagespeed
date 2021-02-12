import requests
import json
from datetime import datetime
import time
import schedule
from pymongo import MongoClient

#client = MongoClient('localhost', 27017)
client = MongoClient('mongo', 27017)
db = client.pagespeed
collection = db.pagespeed_collection

def get_page(url):
    r = requests.get(url)
    if r.ok:  # 200
        print('\nGET PAGE: ' + url)
        return r.text
    print('\nCONNECTION ERROR: ' + str(r.status_code))
    exit(1)  # TODO: 429 code ratelimit error


def encode_key(key):
    return key.replace("\\", "\\\\").replace("\$", "\\u0024").replace(".", "\\u002e")


def decode_key(key):
    return key.replace("\\u002e", ".").replace("\\u0024", "\$").replace("\\\\", "\\")


def check_dict(d):
    new_dict = {}
    for key, value in d.items():
        if isinstance(value, dict):
            value = check_dict(value)
        new_dict[encode_key(key)] = value
    return new_dict


def parse(strategy):    # strategy = 'MOBILE'  # DESKTOP or MOBILE
    api_key = 'AIzaSyA3EpH6c2NciJgIfhP7v3FnoPPBm3wphvA'
    if strategy == 'DESKTOP':
        site = 'https://ura.news'
    else:
        site = 'https://m.ura.news'
    api = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?&strategy=' + strategy + '&key=' + api_key + '&url='
    # api = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?category=SEO&strategy=' + strategy + '&key=' + api_key + '&url='
    url = api + site
    data = check_dict(json.loads(get_page(url)))
    result = {}
    result['pagespeed'] = data
    collection.insert_one(result)


def main():
    # каждые день в 12:00 забирать данные
    schedule.every().day.at("12:00").do(parse, strategy='MOBILE')
    schedule.every().day.at("12:10").do(parse, strategy='DESKTOP')

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()

