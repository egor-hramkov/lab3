import requests

host = 'https://geocode-maps.yandex.ru/1.x/'

params_query = {
    'apikey': '46b49608-1968-44d4-b854-b9fbfcc115ae',
    'geocode': '',
    'format': 'json',
}

city = input()
params_query['geocode'] = city

resp = requests.get(host, params=params_query)
print(resp.status_code)
print(resp.json())
print(resp.reason)
print(resp.url)

with open('data.json', mode='w', encoding='utf8') as f:
    f.write(resp.text)

atitude = ""
latitude = ""
