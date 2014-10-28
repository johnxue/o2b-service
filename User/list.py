from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
from User import user


class Handler(WebRequestHandler):
 
    def post(self): 
        try :
            super().get(self)
            userid=self.getTokenToUser()
            objData=self.getRequestData()
            try :
                data={
                       'user': objData['user'],
                       'password' : objData['pwd'],
                       'mobile' : objData['mbile']
                }
            except :
                raise BaseError(801) # 参数错误
                
            
            db=self.openDB()
            hu=user.userinfo(db)
            userinfo=hu.add(userid)
            self.response(userinfo)
        except BaseError as e:
            self.gotoErrorPage(e.code)


