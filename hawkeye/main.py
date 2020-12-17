import os
import signal

from app import Hawkeye
from config import config

if __name__ == '__main__':
    env = os.getenv('ENV') or 'development'
    conf = config[env]

    clint = Hawkeye(config=conf)
    signal.signal(signal.SIGINT, clint.close_connections)
    signal.signal(signal.SIGTERM, clint.close_connections)

    clint.run()
