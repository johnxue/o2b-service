from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

# 修改用户密码

class Handler(WebRequestHandler):
    def patch(self):
        try :
            super().patch(self)
            user=self.getTokenToUser()
	
            db=self.openDB()

            objData=self.getRequestData()
            conditions = {'user':user, 'password':objData["oldPwd"]}
            db.update('tbUser',{'password':objData["newPwd"]},conditions,lock=False)
            
            self.closeDB()
            self.response() 
        except BaseError as e:
            self.gotoErrorPage(e.code)		
		
	    
