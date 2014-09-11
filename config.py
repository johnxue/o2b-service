import os

App_Key='fb98ab9159f51fd0'
App_Secret='09f7c8cba635f7616bc131b0d8e25947s'

dbConfig = {
  'user': 'root',
  'password': '123456',
  'host': '192.168.1.210',
  'database': 'o2b',
  'raise_on_warnings': True,
}

redisConfig={
    'host':'localhost',
    'port':6379,
    'db':12,
    'password':'jct2014redis',
}

DEBUG = True
LOG_FILENAME = os.path.join(os.path.abspath('./logs/'), 'o2b.log')
LOG_FORMAT = '%(filename)s [%(asctime)s] [%(levelname)s] %(message)s'