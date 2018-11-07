from data import *
import sys, http.client, urllib, json, hashlib, hmac, time, requests

class ExmoAPI:
    def __init__(self, API_KEY, API_SECRET, API_URL='api.exmo.me', API_VERSION='v1'):
        self.API_URL = API_URL
        self.API_VERSION = API_VERSION
        self.API_KEY = API_KEY
        self.API_SECRET = bytes(API_SECRET, encoding='utf-8')

    def sha512(self, data):
        H = hmac.new(key=self.API_SECRET, digestmod=hashlib.sha512)
        H.update(data.encode('utf-8'))
        return H.hexdigest()

    def api_query(self, api_method, params={}):
        params['nonce'] = int(round(time.time() * 1000))
        params = urllib.parse.urlencode(params)

        sign = self.sha512(params)
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Key": self.API_KEY,
            "Sign": sign
        }
        conn = http.client.HTTPSConnection(self.API_URL)
        conn.request("POST", "/" + self.API_VERSION + "/" + api_method, params, headers)
        # print("POST", "/" + self.API_VERSION + "/" + api_method, params, headers)
        response = conn.getresponse().read()

        conn.close()

        try:
            obj = json.loads(response.decode('utf-8'))
            if 'error' in obj and obj['error']:
                print(obj['error'])
                raise sys.exit()
            return obj
        except json.decoder.JSONDecodeError:
            print('Error while parsing response:', response)
            raise sys.exit()
def get_status():
    ExmoAPI_instance = ExmoAPI(ekey, esekret)
    obj = ExmoAPI_instance.api_query('user_info')
    z = {}
    z['return'] = {}
    z['return']['funds'] = {}
    for i in obj['balances']:
        p2 = i.lower()
        z['return']['funds'][p2] = float(obj['balances'][i])
    return z
def get_depth(pair):
    url = 'http://api.exmo.me/v1/order_book/?pair=' + pair.upper() + '&limit=200'
    r = requests.get(url)
    r = r.json()
    z = {}
    for pair in r:
        pair2 = pair.lower()
        z[pair2] = {'asks': [], 'bids': []}
        for i in r[pair]['ask']:
            z[pair2]['asks'].append([float(i[0]), float(i[1])])
        for i in r[pair]['bid']:
            z[pair2]['bids'].append([float(i[0]), float(i[1])])
    return z
def get_my_orders():
    ExmoAPI_instance = ExmoAPI(ekey, esekret)
    obj = ExmoAPI_instance.api_query('user_open_orders')
    z = {}
    z['success'] = 0
    z['error'] = 'all ok'
    z['return'] = {}
    for pair in obj:
        for order in range(len(obj[pair])):
            z['success'] = 1
            oid = obj[pair][order]['order_id']
            p2 = obj[pair][order]['pair'].lower()
            z['return'][oid] = {'pair': p2, 'type': obj[pair][order]['type'],
                                'amount': float(obj[pair][order]['quantity']), 'rate': float(obj[pair][order]['price'])}
    if z['success'] == 0:
        z['error'] = 'no orders'
    return z
def cancel_order(ord):
    ExmoAPI_instance = ExmoAPI(ekey, esekret)
    obj = ExmoAPI_instance.api_query('order_cancel', {'order_id': ord});
    return obj
def trade(type, rate, amount, p):
    ExmoAPI_instance = ExmoAPI(ekey, esekret)
    obj = ExmoAPI_instance.api_query('order_create',
                                     {'type': type, 'price': rate, 'quantity': amount, 'pair': p.upper()});
    return obj
def find_rate(depth, pair, typ, am_lim):
    rate = depth[pair][typ][0][0]
    am_sum = 0.0
    for orders in depth[pair][typ]:
        am = orders[1]
        rate = orders[0]
        am_sum += am
        if am_sum > am_lim:
            break
    return rate
