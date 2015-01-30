from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
from User import entity
import tornado.web
import tornado.gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
import config

class Handler(WebRequestHandler):
    executor = ThreadPoolExecutor(2)
    # 查询
    @tornado.web.asynchronous
    @tornado.gen.coroutine    
    def get(self): 
        try :
            userinfo = yield self.callback_getUserInfo()
            self.response(userinfo)
        except BaseError as e:
            self.gotoErrorPage(e.code)
            
    @run_on_executor
    def callback_getUserInfo(self) :
        try :
            super().get(self)
            userInfo=self.objUserInfo
            userInfo['header']=config.imageConfig['userheader']['url']+'/'+userInfo['header']
            del userInfo['password']
            return userInfo
        except BaseError as e:
            self.gotoErrorPage(e.code)
    
    # 修改        
    def put(self): 
        try :
            super().get(self)
            objData=self.getRequestData()
            user=self.objUserInfo['user']
          
            data={}

            # 昵称不充许修改
            #try :
            #    data={
            #        'nickname'   : objData['n']
            #    }
            #except :
            #    pass
            
            try :
                data['gender']= objData['g']
            except :
                pass
            
            try :
                data['provinceId']= objData['p']
                data['cityId']= objData['c']
            except :
                pass
            
            try :
                data['introduce']= objData['i']
            except :
                pass            
                
            try :
                data['mobile']= objData['m']
            except :
                pass
                
            try :
                data['email']= objData['e']
            except :
                pass              
                
            db=self.openDB()
            hu=entity.user()
            uid=hu.update(data,user,db)
            self.closeDB()            

            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)

        


