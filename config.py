import os

App_Key    = 'fb98ab9159f51fd0'
App_Secret = '09f7c8cba635f7616bc131b0d8e25947s'

# pool_size 最大32
pdbConfig = {
  'pool_name'         : "dbpool",
  'pool_size'         : 16,
  'user'              : 'root',
  'password'          : '123456',
  'host'              : '192.168.1.210',
  'database'          : 'o2b',
  'raise_on_warnings' : True,
}


redisConfig={
    'host'     : '192.168.1.210',
    'port'     : 6379,
    'db'       : 12,
    'password' : 'jct2014redis',
}

imageConfig={
    'product.banner' : {
        'path' : '/var/www/o2b/v1.0.0/app/images/product',
        'url'  : '/images/product',
        'long' : 2560,
        'wide' : 450,
        'size' : 2*1024*1024
    },
    'product.large' : {
            'path' : '/var/www/o2b/v1.0.0/app/images/product',
            'url'  : '/images/product',
            'long' : 468,
            'wide' : 224,
            'size' : 1*1024*1024
    },
    'product.medium' : {
            'path' : '/var/www/o2b/v1.0.0/app/images/product',
            'url'  : '/images/product',
            'long' : 223,
            'wide' : 165,
            'size' : 1*1024*1024
    },
    'product.small' : {
            'path' : '/var/www/o2b/v1.0.0/app/images/product',
            'url'  : '/images/product',
            'long' : 60,
            'wide' : 60,
            'size' : 1*512*1024
    },
    'order.returns' : {
            'path' : '/var/www/o2b/v1.0.0/app/images/returns',
            'url'  : '/images/returns',
            'long' : 1920,
            'wide' : 1080,
            'size' : 2*1024*1024
        },             
    'userheader'  : {
        'path' : '/var/www/o2b/v1.0.0/app/images/header',
        'url'  : '/images/header',
        'long' : 80,
        'wide' : 80,
        'size' : 1*512*1024
        },
    'groupheader'  : {
        'path' : '/var/www/o2b/v1.0.0/app/images/group/header',
        'url'  : '/images/group/header',
        'long' : 80,
        'wide' : 80,
        'size' : 1*512*1024
        },
    'group'  : {
        'path':'/var/www/o2b/v1.0.0/app/images/group',
        'url'  : '/images/group',
        'long':100,
        'wide' : 100,
        'size' : 4*1024*1024
    },
    'news'  : {
        'path':'/var/www/o2b/v1.0.0/app/images/news',
        'url'  : '/images/news',
        'long' :1024,
        'wide' :768,
        'size' : 4*1024*1024
    },    
    'temp' : {
        'path':'/var/www/o2b/v1.0.0/app/images/tmp',
        'url' :'/images/tmp/{yyyy}{mm}{dd}'
    },
    'imageFileType': ['image/gif', 'image/jpeg', 'image/pjpeg', 'image/bmp', 'image/png', 'image/x-png']
}

DEBUG = True
LOG_FILENAME = os.path.join(os.path.abspath('./logs/'), 'o2b.log')
LOG_FORMAT   = '%(filename)s [%(asctime)s] [%(levelname)s] %(message)s'