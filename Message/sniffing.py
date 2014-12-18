from Framework.Base  import WebRequestHandler,BaseError
from Message import entity
import tornado.web
import tornado.gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

class Handler(WebRequestHandler):
    executor = ThreadPoolExecutor(2)
    
    # 用户查询圈子的所有话题例表
    @tornado.web.asynchronous
    @tornado.gen.coroutine    
    def get(self):
        countInfo = yield self.callback_toSniffing()
        self.response(countInfo,async=True)
        
    @run_on_executor
    def callback_toSniffing(self):
        try :
            super().get(self)
            objUser=self.objUserInfo
            user=objUser['user']                   
            #user   =self.getTokenToUser()        
            msg     = entity.Message()
            countInfo = msg.sniffing(user)
            return countInfo
        except BaseError as e:
            self.gotoErrorPage(e.code)       
