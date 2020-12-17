import logging
import pprint

from binance.enums import *
from binance.websockets import BinanceSocketManager

from app.binance.binclient import BinanceClient
from app.db import ext_db


class Hawkeye:
    logger = logging.getLogger(__name__)

    def __init__(self, config):
        self._config = config
        self.conn_keys = []
        self.bm = None

        ext_db.connection()
        self.init_logging()

        self.KLINE_HANDLERS = {
            "BTCUSDT": {
                KLINE_INTERVAL_1MINUTE: self.process_kline_1m,
                KLINE_INTERVAL_5MINUTE: self.process_kline_5m,
            }
        }

    def run(self):
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

    def process_kline_1m(self, msg):
        if msg['k']['x']:  # at each close
            self.logger.info(pprint.pformat(msg))

    def process_kline_5m(self, msg):
        if msg['k']['x']:  # at each close
            self.logger.info(pprint.pformat(msg))

    def process_kline_15m(self, msg):
        if msg['k']['x']:  # at each close
            self.logger.info(pprint.pformat(msg))

    def process_kline_30m(self, msg):
        if msg['k']['x']:  # at each close
            self.logger.info(pprint.pformat(msg))

    def process_kline_1h(self, msg):
        if msg['k']['x']:  # at each close
            self.logger.info(pprint.pformat(msg))

    def process_kline_4h(self, msg):
        if msg['k']['x']:  # at each close
            self.logger.info(pprint.pformat(msg))

    def process_kline_1d(self, msg):
        if msg['k']['x']:  # at each close
            self.logger.info(pprint.pformat(msg))

    def init_logging(self):
        logformat = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'

        logging.basicConfig(format=logformat, level=logging.WARNING)

        if self._config.DEBUG:
            logging.getLogger('app').setLevel(logging.DEBUG)

    def close_connections(self, signum, stack_frame):
        self.logger.info("Gracefully closing open sockets...")

        if self.bm is not None:
            for key in self.conn_keys:
                self.bm.stop_socket(key)

        # program burada neden sonlanmiyor?
