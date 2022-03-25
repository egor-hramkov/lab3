import requests
import typing
import json

host = 'https://geocode-maps.yandex.ru/1.x/'

params_query = {
    'apikey': '46b49608-1968-44d4-b854-b9fbfcc115ae',
    'geocode': '',
    'format': 'json',
}
params_query_2 = {
    'll': '',
    'spn': '',
    'l': 'map',
}

city = input()
params_query['geocode'] = city

resp = requests.get(host, params=params_query)

if resp.status_code == 200:
    with open('data.json', mode='w', encoding='utf8') as f:
        f.write(resp.text)

    data = resp.json()['response']["GeoObjectCollection"]["featureMember"]
    if data != []:
        coordinates = data[0]["GeoObject"]["Point"]["pos"]  # type: str
        atitude = tuple(coordinates.split(" "))
        print(atitude)

        host = 'https://static-maps.yandex.ru/1.x/'

        if(len(city.split()) == 1):
            params_query_2['spn'] = '0.1646,0.0619'
        else:
            params_query_2['spn'] = '0.0100,0.00100'

        params_query_2['ll'] = atitude[0] + ','
        params_query_2['ll'] += atitude[1]
        resp = requests.get(host, params=params_query_2)
        if resp.status_code == 200:
            with open('map.png', mode='wb') as f:
                f.write(resp.content)



    else:
        print("К сожалению, по вашему запросу ничего не нашлось!!!")
else:
    print("Ошибка: ", resp.status_code)