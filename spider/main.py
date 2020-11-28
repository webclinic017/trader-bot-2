import os

from app import Spider
from config import config

if __name__ == '__main__':
    env = os.getenv('ENV') or 'development'
    conf = config[env]

    peter = Spider(config=conf)
    peter.run()
