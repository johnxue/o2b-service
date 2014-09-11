import os
import ssl
from tornado.httpserver import HTTPServer
import tornado.ioloop
import tornado.web

import mysql.connector

config = {
  'user': 'scott',
  'password': 'tiger',
  'host': '127.0.0.1',
  'database': 'employees',
  'raise_on_warnings': True,
}

cnx = mysql.connector.connect(**config)

cnx.close()



class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world\n")


application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    server = HTTPServer(application,ssl_options={
           "certfile": os.path.join(os.path.abspath("."), "server_localhost.crt"),
           "keyfile": os.path.join(os.path.abspath("."), "server_localhost.key"),
    	})
    server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
