from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
from AdSense import entity

import tornado.web
import tornado.gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

class info(WebRequestHandler):
    executor = ThreadPoolExecutor(2)
    
    @tornado.web.asynchronous
    @tornado.gen.coroutine    
    def get(self):
        try :
            self.checkAppKey()
            rows = yield self.callback_get()
            self.response(rows)
        except BaseError as e:
            self.gotoErrorPage(e.code)

    @run_on_executor
    def callback_get(self):
        db=self.openDB()
        ads=entity.adsense()
        objCodeList=ads.getAttribute(db)
        self.closeDB()
        return objCodeList
