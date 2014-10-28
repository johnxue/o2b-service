import os.path
import ssl
import tornado.httpserver
import tornado.web  
import tornado.ioloop  
import tornado.options  
from tornado.options import define, options  

import logging  
import route


import Framework.dbMysql,Framework.dbRedis,config

from Framework.Base  import BaseError


define("port", default=8081, help="run port", type=int)

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates")  
STATIC_PATH   = os.path.join(os.path.dirname(__file__), "static")


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        raise tornado.web.HTTPError(404)
        
class MyFile(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache")

class Application(tornado.web.Application):  
    def __init__(self):  
        dbConfig    = config.DbConfig        # 得到 DB Config
        redisConfig = config.RedisConfig     # 得到 Redis Config
        
        settings = dict(                     # 得到模板及静态地址路径
            template_path = TEMPLATE_PATH,   
            static_path = STATIC_PATH,   
            debug = True  #开启调试模式
        )
        
        handlers    = route.handlers                                      # 注入路由
        tornado.web.Application.__init__(self, handlers, **settings)  
        self.db  = Framework.dbMysql.DB(dbConfig)                         # 注入MySql
        #self.rds = Framework.dbRedis.RedisCache(redisConfig)              # 注入Redis
        
def main():  
    tornado.options.parse_command_line()  
    app = tornado.httpserver.HTTPServer(Application())
    app.listen(options.port)  
    tornado.ioloop.IOLoop.instance().start()


def sslMain():  
    #if config.DEBUG :
    #    logging.basicConfig(filename=config.LOG_FILENAME,format=config.LOG_FORMAT,datefmt='%y-%m-%d %H:%M:%S',level=logging.DEBUG)

    #tornado.options.options.logging = "debug"  #注意parse_command_line(默认层级为info)对logging层级的影响
    tornado.options.parse_command_line()  
    app = tornado.httpserver.HTTPServer(Application(),ssl_options={
           "certfile": os.path.join(os.path.abspath("./ca/"), "server210.crt"),
           "keyfile": os.path.join(os.path.abspath("./ca/"), "server210.key"),
    	}) 
    app.listen(options.port)  
    tornado.ioloop.IOLoop.instance().start()  


if __name__ == "__main__":
    main()
    
