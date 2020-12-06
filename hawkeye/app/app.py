import logging

from app.binance.binclient import BinanceClient
from app.db import ext_db


class Hawkeye:
    logger = logging.getLogger(__name__)

    def __init__(self, config):
        self._config = config

        ext_db.connection()
        self.init_logging()

    def run(self):
        # get parameters from the table optimized_params
        # test strategy with given params via backtrader
        bin_client = BinanceClient(self._config)
        bin_client.get_open_orders()
        pass

    def init_logging(self):
        logformat = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'

        logging.basicConfig(format=logformat, level=logging.WARNING)

        if self._config.DEBUG:
            logging.getLogger('app').setLevel(logging.DEBUG)
