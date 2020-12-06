import logging
from os import environ

from binance.client import Client


class BinanceClient:
    logger = logging.getLogger(__name__)

    def __init__(self, config):
        self._config = config

        self._api_key = environ.get('API_KEY') or ''
        self._api_secret = environ.get('API_SECRET') or ''
        self.client = Client(self._api_key, self._api_secret)

    def get_open_orders(self):
        # test = [
        #     {
        #         'symbol': 'ENJBTC', 'orderId': 131354691, 'orderListId': -1,
        #         'clientOrderId': 'web_a205529dc8d9487cb557255146158df5', 'price': '0.00003821',
        #         'origQty': '100.00000000', 'executedQty': '0.00000000', 'cummulativeQuoteQty': '0.00000000',
        #         'status': 'NEW', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'stopPrice': '0.00000000',
        #         'icebergQty': '0.00000000', 'time': 1607290013782, 'updateTime': 1607290013782, 'isWorking': True,
        #         'origQuoteOrderQty': '0.00000000'
        #     }
        # ]
        a = self.client.get_open_orders(symbol='ENJBTC')
        print(a)
        exit()
