import os

from app import Spider
from config import config

if __name__ == '__main__':
    env = os.getenv('ENV') or 'development'
    conf = config[env]

    peter = Spider(config=conf)
    peter.run()


# TODO
# Backtrader'ın farkli class'a alinmasi
# Strateji sonuclarindan rahber tablo üretilmesi
# Veritabanindaki son verilerin guncellenmesi
# Farklı farklı bir sürü strateji
