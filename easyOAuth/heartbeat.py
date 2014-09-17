import tornado.web
from dbMysql import dbMysql
import config
import json
from easyOAuth.userinfo import Token

# 
class Handler(tornado.web.RequestHandler):
    
    def gotoErrorPage(self,error_code) :
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,PATCH')
        self.set_header('Access-Control-Allow-Headers', 'app-key,authorization,Content-type')
        self.redirect('/o2b/v1.0.0/error/%d'% error_code )
        
    def checkAppKey(self):
        if self.request.headers.get('app-key')!=config.App_Key :
            r = False
        else :
            r = True
        return r
        
        
    def resetToken(self):
        token=self.request.headers.get('Authorization')
        if token is not None  :
            try :
                myToken=Token(config.redisConfig)
                user=myToken.getUser(token).decode('utf-8')
                myToken.saveToRedis(token,user)
                time=36000
            except:
                time=0
        else :
            time=0
        return time
    


    def options(self,id=''):
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,PATCH')
        self.set_header('Access-Control-Allow-Headers', 'app-key,authorization,Content-type')
      

    def patch(self):  # 用户心跳

        if not self.checkAppKey() :
            # 601 : 未经授权的第三方应用
            self.gotoErrorPage(601)
            return
        
        #token=self.request.headers.get('Authorization')

        time=self.resetToken()
        if time<=0 :
            # 601 : 未经授权的第三方应用
            self.gotoErrorPage(601)
            return            
            
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_status(201)  # 201 操作成功
        self.write('%s' % (time))
        return

 