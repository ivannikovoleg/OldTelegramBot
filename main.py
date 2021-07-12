import requests
import json
import nicehash
from requests import Timeout, TooManyRedirects
from flask import Flask
from flask import request
from flask import jsonify
from flask_sslify import SSLify

app = Flask(__name__)
sslify = SSLify(app)
URL = 'https://api.telegram.org/bot'


def get_json_data(link):
    return requests.get(link).json()


def get_cryptovalues(jsondata, id, val):
    return str(jsondata['data'][id]['quotes']['USD'][val])


def get_crypto_currncies():
    cr_tuple = ('1', '1027', '1831', '328', '1437')
    build = ''
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
        'id': '1,1027,1831,328,1437'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': 'API-KEY'
    }
    session = requests.Session()
    session.headers.update(headers)
    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        for x in cr_tuple:
            build += str(data['data'][x]['symbol']) + ': ' \
                     + str(round(float(data['data'][x]['quote']['USD']['price']), 2)) + '$ 24h: ' \
                     + str(round(float(data['data'][x]['quote']['USD']['percent_change_24h']), 2)) + '%\n'
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    return build


def get_unpaid_ballance():
    nhbvalue = get_json_data('https://api.nicehash.com/'
                           'api?method=stats.provider&addr=wallet')
    return 'Unpaid balance: {} btc'.format(str(nhbvalue['result']['stats'][1]['balance']))


def get_workers_online():
    build = ''
    host = 'https://api2.nicehash.com'
    org_id = 'org_id'
    key = 'key'
    secret = 'secret'
    private_api = nicehash.private_api(host, org_id, key, secret)
    my_workers = private_api.get_rigs2()
    for x in range(int(my_workers['minerStatuses']['MINING'])):
        build += my_workers['miningRigs'][x]['name'] + ' '
    return 'Miners online: ' + build


def get_exchange_rate():
    curvalue = get_json_data('http://data.fixer.io/api/latest?access_key=access_key&symbols=USD,RUB,UAH')
    rte = 'RUB to EUR: {}р.\n'.format(round(curvalue['rates']['RUB'], 2))
    rtu = 'RUB to USD: {}р.\n'.format(round(curvalue['rates']['RUB'] / curvalue['rates']['USD'], 2))
    rtg = 'RUB to UAH: {}р.'.format(round(curvalue['rates']['RUB'] / curvalue['rates']['UAH'], 2))
    str = rte + rtu + rtg
    return str


def send_message(chat_id, text='hello'):
    url = URL + 'sendMessage'
    answer = {'chat_id': chat_id, 'text': text}
    r = requests.post(url, json=answer)
    return r.json()


@app.route('/route', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        r = request.get_json()
        chat_id = r['message']['chat']['id']
        message = r['message']['text']
        if 'crypto' in message:
            send_message(chat_id, text=get_crypto_currncies())
        elif 'workers' in message:
            send_message(chat_id, text=get_workers_online())
        elif 'balance' in message:
            send_message(chat_id, text=get_unpaid_ballance())
        elif 'currencies' in message:
            send_message(chat_id, text=get_exchange_rate())
        return jsonify(r)
    return '<h1>Hello stranger</h1>'


if __name__ == '__main__':
    app.run()
