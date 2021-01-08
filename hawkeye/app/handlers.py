from app.models.historical_data import HistoricalData


def process_kline_1m(msg):
    closed = msg['k']['x']
    kline_data = None

    if closed:
        kline_data = convert(msg['k'])
        kline_data.insert()

    if kline_data is not None:
        _postprocess(kline_data.symbol, kline_data.interval)


def process_kline_5m(msg):
    if msg['k']['x']:  # at each close
        kline_data = convert(msg['k'])


def _postprocess(symbol, interval):
    # get strategy & params for this symbol & interval
    pass



def convert(kl) -> HistoricalData:
    """
    Ref. https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-streams
    """
    data = {
        'symbol': kl['s'],
        'interval': kl['i'],
        'open_time': kl['t'] / 1000,
        'open': kl['o'],
        'high': kl['h'],
        'low': kl['l'],
        'close': kl['c'],
        'volume': kl['v'],
        'close_time': kl['T'] / 1000,
        'number_of_trades': kl['n']
    }

    return HistoricalData(**data)
