from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
from User import entity
import tornado.web
import tornado.gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

class Handler(WebRequestHandler):
    executor = ThreadPoolExecutor(2)
    
    @tornado.web.asynchronous
    @tornado.gen.coroutine    
    def get(self,userid): 
        try :
            userinfo = yield self.callback_getUserInfo()
            self.response(userinfo)
        except BaseError as e:
            self.gotoErrorPage(e.code)
            
    @run_on_executor
    def callback_getUserInfo(self) :
        try :
            super().get(self)
            return self.objUserInfo
        except BaseError as e:
            self.gotoErrorPage(e.code)
        


