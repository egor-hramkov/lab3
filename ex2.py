from flask import Flask, url_for, render_template
from werkzeug.utils import redirect
import requests
app = Flask(__name__)

host = 'https://geocode-maps.yandex.ru/1.x/'
host2 = 'https://static-maps.yandex.ru/1.x/'




@app.route('/')
def index():
    return redirect(url_for('city_map'))

@app.route('/city_map/<city>/')
@app.route('/city_map/')
def city_map(city='Ульяновск'):
    data = []
    message = ''
    path_png = 'map2.png'
    params_query = {
        'apikey': '46b49608-1968-44d4-b854-b9fbfcc115ae',
        'geocode': '',
        'format': 'json',
    }
    params_query_2 = {
        'll': '',
        'spn': '0.1646,0.0619',
        'l': 'map',
    }

    params_query['geocode'] = city
    resp = requests.get(host, params=params_query)
    with open('data2.json', mode='w', encoding='utf8') as f:
        f.write(resp.text)

    data = (resp.json()['response']["GeoObjectCollection"]["featureMember"])
    if data != []:
        coordinates = data[0]["GeoObject"]["Point"]["pos"]  # type: str
        atitude = tuple(coordinates.split(" "))
        country = data[0]["GeoObject"]['metaDataProperty']['GeocoderMetaData']['Address']["Components"][0]['name']
        province = data[0]["GeoObject"]['metaDataProperty']['GeocoderMetaData']['Address']["Components"][2]['name']
        county = data[0]["GeoObject"]['metaDataProperty']['GeocoderMetaData']['Address']["Components"][1]['name']
        params_query_2['ll'] = atitude[0] + ','
        params_query_2['ll'] += atitude[1]
        resp = requests.get(host2, params=params_query_2)
        with open('map2.png', mode='wb') as f:
            f.write(resp.content)
    else:
        city = '-'
        country = '-'
        province = '-'
        county = '-'
        message = 'Вы ввели несуществующий город!'
    return render_template('index.html', city=city, country = country, province = province, county = county, message = message, data=data)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')

