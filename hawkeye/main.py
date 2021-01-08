import os

from app import Hawkeye
from config import config

if __name__ == '__main__':
    env = os.getenv('ENV') or 'development'
    conf = config[env]

    clint = Hawkeye(config=conf)

    try:
        # clint.run()
        clint.main2()
    except KeyboardInterrupt:
        clint.close_connections()
