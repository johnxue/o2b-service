from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
from User import user


class Handler(WebRequestHandler):
 
    def get(self,userid): 
        try :
            super().get(self)
            userid=self.getTokenToUser()
            
            db=self.openDB()
            hu=user.userinfo(db)
            userinfo=hu.get(userid)
            self.response(userinfo)
        except BaseError as e:
            self.gotoErrorPage(e.code)


