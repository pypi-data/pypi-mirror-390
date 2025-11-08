#!/usr/bin/env python3

import requests
import re
import random
import string
from datetime import date
from json import loads, dumps

def get_random_hash():
    random_source = string.ascii_letters + string.digits
    password = ''

    # generate other characters
    for i in range(16):
        password += random.choice(random_source)

    password_list = list(password)
    # shuffle all characters
    random.SystemRandom().shuffle(password_list)
    password = ''.join(password_list)
    return password

result = {}

print('start')

session = requests.Session()
hash = get_random_hash()
url = 'https://api-auth.dom.ru/v1/person/auth'

# Login part
data = {
    'username' : '630021536300',
    'password' : 'bn3hhk5b'
}

headers = {
    'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundary${hash}',
    'Domain': 'samara',
    'Origin': 'https://samara.dom.ru',
    'Referer': 'https://samara.dom.ru/',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15'
}

body = """------WebKitFormBoundary${hash}
Content-Disposition: form-data; name="username"

""" + data['username'] + """
------WebKitFormBoundary${hash}
Content-Disposition: form-data; name="password"

""" + data['password'] + """
------WebKitFormBoundary${hash}
Content-Disposition: form-data; name="rememberMe"

1
------WebKitFormBoundary${hash}--"""

auth = session.post(url, headers=headers, data=body)
print(auth)
auth_data = loads( auth.text )

print(auth_data)

if auth_data['status'] == 1:
    access_token = auth_data['data']['access_token']
    refresh_token = auth_data['data']['refresh_token']
    city_domain = auth_data['data']['billing_domain']
    provider_id = str( auth_data['data']['provider_id'] )

    headers.pop("Content-Type")
    headers['Authorization'] = 'Bearer ' + access_token
    headers['ProviderId'] = provider_id

    today = date.today().strftime("%d.%m.%Y")
    payments = session.get(
        "https://api-profile.dom.ru/v1/payments/period-structure?date_from=" + today + "&newApi=true", 
        headers=headers
    )

    payments_data = loads( payments.text )

    if payments_data['data']['status'] == 1:
        header_info = payments_data['data']['result']['GetPeriodStructure']['HeaderInfo']
        result['planName'] = header_info['plans'][0]['name'].replace('"', '') + ' (' + header_info['plans'][0]['speed'].replace('"', '') + ')'
        result['paid'] = header_info['PeriodRow']
        result['personalAccount'] = header_info['AgrNumber']

        balance = session.get(
            "https://api-profile.dom.ru/v1/info/payment", 
            headers=headers
        )
        balance_data = loads( balance.text )

        result['balance'] = balance_data['balance']
        print( dumps(result) )
    else:
        print( dumps(result) )
else:
    print( dumps(result) )
