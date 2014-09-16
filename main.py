import os
import ssl
from tornado.httpserver import HTTPServer
import tornado.ioloop
import tornado.web
import logging
import config

import Error

import easyOAuth.login
import easyOAuth.logout
import easyOAuth.heartbeat

import Product.attribute
import Product.list
import Product.detail
import Product.follow

import Address.list
import Address.userAddress

import AdSense.list

import News.list
import News.detail

import ShoppingCart.list

import Order.list
import Order.detail
import Order.attribute
import Order.Returns.list


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world\n")
        
class MyFile(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache")

settings = {'debug' : True}  #开启调试模式

application = tornado.web.Application([
    (r"/o2b/", MainHandler),
    
    (r"/o2b/v1.0.0/news", News.list.info),
    (r"/o2b/v1.0.0/news/([0-9]+)", News.detail.info),
    
    (r"/o2b/v1.0.0/area", Address.list.info),
    (r"/o2b/v1.0.0/address", Address.userAddress.list),
    (r"/o2b/v1.0.0/address/([0-9]+)", Address.userAddress.list),

    (r"/o2b/v1.0.0/login/(.*)/(.*)", easyOAuth.login.Handler),
    (r"/o2b/v1.0.0/logout", easyOAuth.logout.Handler),
    (r"/o2b/v1.0.0/service/heartbeat", easyOAuth.heartbeat.Handler),

    (r"/o2b/v1.0.0/product/([0-9]+)/follow", Product.follow.hFollow),
    (r"/o2b/v1.0.0/product/([0-9]+)", Product.detail.info),
    (r"/o2b/v1.0.0/product/attribute", Product.attribute.info),
    (r"/o2b/v1.0.0/product", Product.list.info),
    
    (r"/o2b/v1.0.0/shoppingcart", ShoppingCart.list.info),
    
    (r"/o2b/v1.0.0/order", Order.list.info),
    (r"/o2b/v1.0.0/order/([0-9]+)", Order.detail.info),
    (r"/o2b/v1.0.0/order/attribute", Order.attribute.info),
    (r"/o2b/v1.0.0/order/returns", Order.Returns.list.info),

    (r"/o2b/v1.0.0/adSense/(.*)/([0-9]+)", AdSense.list.info),

    (r"/o2b/v1.0.0/error/([0-9]+)", Error.Handler),
    

],**settings)



if __name__ == "__main__":
    application.listen(8081)
    tornado.ioloop.IOLoop.instance().start()

'''

if __name__ == "__main__":
    
    if config.DEBUG :
        logging.basicConfig(filename=config.LOG_FILENAME,format=config.LOG_FORMAT,datefmt='%y-%m-%d %H:%M:%S',level=logging.DEBUG)
        
    server = HTTPServer(application,ssl_options={
           "certfile": os.path.join(os.path.abspath("./ca/"), "server210.crt"),
           "keyfile": os.path.join(os.path.abspath("./ca/"), "server210.key"),
    	})
    

    server.listen(8081)
    tornado.ioloop.IOLoop.instance().start()
'''
