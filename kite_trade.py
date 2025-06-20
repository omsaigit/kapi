import os
try:
    import requests,json
except ImportError:
    os.system('python -m pip install requests')
try:
    import dateutil
except ImportError:
    os.system('python -m pip install python-dateutil')

import requests
import dateutil.parser


def get_enctoken(userid, password, twofa):
    session = requests.Session()
    response = session.post('https://kite.zerodha.com/api/login', data={
        "user_id": userid,
        "password": password
    })
    response = session.post('https://kite.zerodha.com/api/twofa', data={
        "request_id": response.json()['data']['request_id'],
        "twofa_value": twofa,
        "user_id": response.json()['data']['user_id']
    })
    enctoken = response.cookies.get('enctoken')
    if enctoken:
        return enctoken
    else:
        raise Exception("Enter valid details !!!!")


class KiteApp:
    # Products
    PRODUCT_MIS = "MIS"
    PRODUCT_CNC = "CNC"
    PRODUCT_NRML = "NRML"
    PRODUCT_CO = "CO"

    # Order types
    ORDER_TYPE_MARKET = "MARKET"
    ORDER_TYPE_LIMIT = "LIMIT"
    ORDER_TYPE_SLM = "SL-M"
    ORDER_TYPE_SL = "SL"

    # Varities
    VARIETY_REGULAR = "regular"
    VARIETY_CO = "co"
    VARIETY_AMO = "amo"

    # Transaction type
    TRANSACTION_TYPE_BUY = "BUY"
    TRANSACTION_TYPE_SELL = "SELL"

    # Validity
    VALIDITY_DAY = "DAY"
    VALIDITY_IOC = "IOC"

    # Exchanges
    EXCHANGE_NSE = "NSE"
    EXCHANGE_BSE = "BSE"
    EXCHANGE_NFO = "NFO"
    EXCHANGE_CDS = "CDS"
    EXCHANGE_BFO = "BFO"
    EXCHANGE_MCX = "MCX"

    def __init__(self, enctoken):
        # self.headers = {"Authorization": f"enctoken {enctoken}"}
        # self.session = requests.session()
        # # self.root_url = "https://api.kite.trade"
        # self.root_url = "https://kite.zerodha.com/oms"
        # self.session.get(self.root_url, headers=self.headers)
        # new
        self.enctoken = enctoken
        self.headers = {
            "x-kite-version": "3",
            'Authorization': 'enctoken {}'.format(self.enctoken)
        }
        self.session = requests.session()
        self.api_key = "kite"
        self.user_id = "KK7143"
        self.root2 = "https://kite.zerodha.com/oms"
        self.root_url_new = "https://api.kite.trade"
        self.root_url = "https://kite.zerodha.com/oms"


        self.session.get(self.root_url, headers=self.headers)
        # KiteConnect.__init__(self, api_key="kite")

    def instruments(self, exchange=None):
        response = self.session.get(f"{self.root_url_new}/instruments", headers=self.headers)
        print("Raw response text:", response.text[:500])  # Print first 500 chars for inspection
        data = response.text.split("\n")
        print("Instrument CSV lines:", len(data))
        Exchange = []
        for i in data[1:-1]:
            row = i.split(",")
            if exchange is None or exchange == row[11]:
                Exchange.append({
                    'instrument_token': int(row[0]),
                    'exchange_token': row[1],
                    'tradingsymbol': row[2],
                    'name': row[3][1:-1],
                    'last_price': float(row[4]),
                    'expiry': dateutil.parser.parse(row[5]).date() if row[5] != "" else None,
                    'strike': float(row[6]),
                    'tick_size': float(row[7]),
                    'lot_size': int(row[8]),
                    'instrument_type': row[9],
                    'segment': row[10],
                    'exchange': row[11]
                })
        print("Parsed instruments:", len(Exchange))
        return Exchange

    def quote(self, instruments):
        data = self.session.get(f"{self.root_url}/quote", params={"i": instruments}, headers=self.headers).json()["data"]
        return data

    def ltp(self, instruments):
        data = self.session.get(f"{self.root_url}/quote/ltp", params={"i": instruments}, headers=self.headers).json()
        return data

    def historical_data(self, instrument_token, from_date, to_date, interval, continuous=False, oi=False):
        params = {"from": from_date,
                  "to": to_date,
                  "interval": interval,
                  "continuous": 1 if continuous else 0,
                  "oi": 1 if oi else 0}
        lst = self.session.get(
            f"{self.root_url}/instruments/historical/{instrument_token}/{interval}", params=params,
            headers=self.headers).json()["data"]["candles"]
        records = []
        for i in lst:
            record = {"date": dateutil.parser.parse(i[0]), "open": i[1], "high": i[2], "low": i[3],
                      "close": i[4], "volume": i[5],}
            if len(i) == 7:
                record["oi"] = i[6]
            records.append(record)
        return records

    def historical_data_v2(self, instrument_token, from_date, to_date, interval="minute", oi=False):
        """
        Fetch historical data using the new URL format
        Args:
            instrument_token: The instrument token
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            interval: Data interval (default: minute)
            oi: Include OI data (default: False)
        """
        params = {
            "user_id": self.user_id,
            "from": from_date,
            "to": to_date,
            "oi": 1 if oi else 0
        }
        
        response = self.session.get(
            f"{self.root2}/instruments/historical/{instrument_token}/{interval}",
            params=params,
            headers=self.headers
        ).json()
        # print("response",response)
        if "data" in response and "candles" in response["data"]:
            records = []
            for candle in response["data"]["candles"]:
                record = {
                    "date": dateutil.parser.parse(candle[0]),
                    "open": candle[1],
                    "high": candle[2],
                    "low": candle[3],
                    "close": candle[4],
                    "volume": candle[5]
                }
                if len(candle) == 7:
                    record["oi"] = candle[6]
                records.append(record)
            return records
        return []

    def margins(self):
        margins = self.session.get(f"{self.root_url}/user/margins", headers=self.headers).json()["data"]
        return margins
    def profile(self):
        profile = self.session.get(f"{self.root_url}/user/profile/full", headers=self.headers).json()["data"]
        return profile
    def orders(self):
        orders = self.session.get(f"{self.root_url}/orders", headers=self.headers).json()["data"]
        return orders

    def positions(self):
        positions = self.session.get(f"{self.root_url}/portfolio/positions", headers=self.headers).json()["data"]
        return positions
    def profile(self):
        profile = self.session.get(f"{self.root_url}/user/profile/full", headers=self.headers).json()["data"]
        return profile
    
    def holdings(self):
        holdings = self.session.get(f"{self.root_url}/portfolio/holdings", headers=self.headers).json()["data"]
        return holdings

    def place_order(self, variety, exchange, tradingsymbol, transaction_type, quantity, product, order_type, price=None,
                    validity=None, disclosed_quantity=None, trigger_price=None, squareoff=None, stoploss=None,
                    trailing_stoploss=None, tag=None):
        params = locals()
        del params["self"]
        for k in list(params.keys()):
            if params[k] is None:
                del params[k]
        order_id = self.session.post(f"{self.root_url}/orders/{variety}",
                                     data=params, headers=self.headers).json()["data"]["order_id"]
        return order_id

    def modify_order(self, variety, order_id, parent_order_id=None, quantity=None, price=None, order_type=None,
                     trigger_price=None, validity=None, disclosed_quantity=None):
        params = locals()
        del params["self"]
        for k in list(params.keys()):
            if params[k] is None:
                del params[k]

        order_id = self.session.put(f"{self.root_url}/orders/{variety}/{order_id}",
                                    data=params, headers=self.headers).json()["data"][
            "order_id"]
        return order_id

    def cancel_order(self, variety, order_id, parent_order_id=None):
        order_id = self.session.delete(f"{self.root_url}/orders/{variety}/{order_id}",
                                       data={"parent_order_id": parent_order_id} if parent_order_id else {},
                                       headers=self.headers).json()["data"]["order_id"]
        return order_id
    

    def buy_equity(self, tradingsymbol, quantity,transaction_type,tag=None):
        variety='regular'
        params ={    'exchange': 'NSE', 
                     'tradingsymbol': tradingsymbol, 
                     'transaction_type': transaction_type, 
                     'quantity': quantity, 
                     'product': 'CNC', 
                     'order_type': 'MARKET', 
                     'tag': tag
                }
        reponse = self.session.post(f"{self.root_url}/orders/{variety}",
                                     data=params, headers=self.headers).json()
        return reponse

    def buy(self, tradingsymbol, quantity,transaction_type,tag=None):
        variety='regular'
        params ={    'exchange': 'NFO', 
                     'tradingsymbol': tradingsymbol, 
                     'transaction_type': transaction_type, 
                     'quantity': quantity, 
                     'product': 'MIS', 
                     'order_type': 'MARKET', 
                     'tag': tag
                }
        reponse = self.session.post(f"{self.root_url}/orders/{variety}",
                                     data=params, headers=self.headers).json()
        return reponse
    def buy_limit(self, tradingsymbol, quantity,price,transaction_type,tag=None):
        variety='regular'
        params ={    'exchange': 'NFO', 
                        'tradingsymbol': tradingsymbol, 
                        'transaction_type': transaction_type, 
                        'quantity': quantity, 
                        'product': 'MIS', 
                        'price':price,
                        'order_type': 'LIMIT', 
                        'tag': tag
                }
        reponse = self.session.post(f"{self.root_url}/orders/{variety}",
                                        data=params, headers=self.headers).json()
        return reponse
    
    def sell_target(self, tradingsymbol, quantity,price,tag=None):
        variety='regular'
        params ={    'exchange': 'NFO', 
                     'tradingsymbol': tradingsymbol, 
                     'transaction_type': 'SELL', 
                     'price':price,
                     'quantity': quantity, 
                     'product': 'MIS', 
                     'order_type': 'LIMIT', 
                     'tag': tag
                }
        reponse = self.session.post(f"{self.root_url}/orders/{variety}",data=params, headers=self.headers).json()
        return reponse
    
    def sell_sl(self, tradingsymbol, quantity,price,trigger_price,tag=None):
        variety='regular'
        params ={    'exchange': 'NFO', 
                    'tradingsymbol': tradingsymbol, 
                    'transaction_type': 'SELL', 
                    'price':price,
                    'trigger_price':trigger_price,
                    'quantity': quantity, 
                    'product': 'MIS', 
                    'order_type': 'SL', 
                    'tag': tag
            }
        reponse = self.session.post(f"{self.root_url}/orders/{variety}",data=params, headers=self.headers).json()
        return reponse
    
    def modify_order_exit(self, order_id, quantity):
        variety='regular'
        params={'order_id':order_id,
                'quantity':quantity,
                'order_type':'MARKET',
                'validity':'DAY'}
        response = self.session.put(f"{self.root_url}/orders/{variety}/{order_id}",
                                    data=params, headers=self.headers).json()
        return response