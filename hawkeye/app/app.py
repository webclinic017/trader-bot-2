import logging
import pprint

from binance.enums import *
from binance.websockets import BinanceSocketManager

from app.models import OptimizedParams
from app.binance.binclient import BinanceClient
from app.db import ext_db
from app.handlers import *


class Hawkeye:
    logger = logging.getLogger(__name__)

    KLINE_HANDLERS = {
        "BTCUSDT": {
            KLINE_INTERVAL_1MINUTE: process_kline_1m,
            # KLINE_INTERVAL_5MINUTE: process_kline_5m,
        }
    }

    def __init__(self, config):
        self._config = config
        self.conn_keys = []
        self.bm = None

        ext_db.connection()
        self.init_logging()

    def listen(self):
        # get parameters from the table optimized_params
        # test strategy with given params via backtrader
        bin_client = BinanceClient(self._config)
        self.bm = BinanceSocketManager(bin_client)
        self.register_sockets()

        self.logger.info("Starting socket connections...")
        self.bm.start()
        self.logger.info("Started socket connections.")

    def register_sockets(self):
        for symbol in self.KLINE_HANDLERS:
            for interval in self.KLINE_HANDLERS[symbol]:
                handler = self.KLINE_HANDLERS[symbol][interval]

                self.conn_keys.append(
                    self.bm.start_kline_socket(symbol, handler, interval=interval))

                self.logger.info(f"Registered socket for {symbol} - {interval}")

    def init_logging(self):
        logformat = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'

        logging.basicConfig(format=logformat, level=logging.WARNING)

        if self._config.DEBUG:
            logging.getLogger('app').setLevel(logging.DEBUG)

    def close_connections(self):
        self.logger.info("Gracefully closing open sockets...")

        if self.bm is not None:
            for key in self.conn_keys:
                self.bm.stop_socket(key)

        # program burada neden sonlanmiyor?

    def run(self):
        import backtrader as bt
        from os import environ
        import datetime as dt
        import time
        from app.strategies.pmax import PMaxStrategy
        from app.ccxtbt import CCXTStore

        # import ccxt
        # binance = ccxt.binance({
        #     'apiKey': environ.get('API_KEY_TEST') or '',
        #     'secret': environ.get('API_SECRET_TEST') or '',
        #     'verbose': True,
        # })
        # binance.set_sandbox_mode(True)
        # print(binance.create_market_sell_order('BTC/USDT', 0.00111675))
        # exit(0)

        cerebro = bt.Cerebro(quicknotify=True)
        broker_config = {
            'apiKey': environ.get('API_KEY_TEST') or '',
            'secret': environ.get('API_SECRET_TEST') or '',
            'nonce': lambda: str(int(time.time() * 1000)),
            'enableRateLimit': True,
        }
        sandbox = True

        store = CCXTStore(exchange='binance',
                          currency='USDT',
                          config=broker_config,
                          retries=5,
                          debug=False,
                          sandbox=sandbox)

        if sandbox:
            # override public url to fetch klines from original api instead of testnet
            store.exchange.urls['api']['public'] = 'https://api.binance.com/api/v3'

        broker_mapping = {
            'order_types': {
                bt.Order.Market: 'market',
                bt.Order.Limit: 'limit',
                bt.Order.Stop: 'stop-loss',  # stop-loss for kraken, stop for bitmex
                bt.Order.StopLimit: 'stop limit'
            },
            'mappings': {
                'closed_order': {
                    'key': 'status',
                    'value': 'closed'
                },
                'canceled_order': {
                    'key': 'status',
                    'value': 'canceled'
                }
            }
        }

        broker = store.getbroker(broker_mapping=broker_mapping)
        cerebro.setbroker(broker)

        hist_start_date = dt.datetime.utcnow() - dt.timedelta(minutes=300)  # burasi max 1000 olmali
        data = store.getdata(
            dataname='BTC/USDT',
            name="BTCUSDT",
            timeframe=bt.TimeFrame.Minutes,
            fromdate=hist_start_date,
            compression=1,
            ohlcv_limit=99999
        )
        cerebro.adddata(data)
        oparam: OptimizedParams = OptimizedParams.get(OptimizedParams.symbol == "BTCUSDT", OptimizedParams.interval == "15m")
        params = oparam.parameters

        params = {"period": 1, "multiplier": 0.5, "length": 1, "mav": "sma", "printlog": True}

        cerebro.addstrategy(PMaxStrategy, **params)

        initial_value = cerebro.broker.getvalue()
        print('Starting Portfolio Value: %.2f' % initial_value)
        result = cerebro.run()
        final_value = cerebro.broker.getvalue()
        print('Final Portfolio Value: %.2f' % final_value)
