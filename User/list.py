from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
from User import entity



class Handler(WebRequestHandler):
 
    def post(self): 
        try :
            super().get(self)
            userid=self.getTokenToUser()
            objData=self.getRequestData()
            try :
                data={
                       'user'     : objData['user'],
                       'password' : objData['pwd'],
                       'mobile'   : objData['mobile'],
                       'header'   : objData['header']
                }
            except :
                raise BaseError(801) # 参数错误
            
            hu=entity.user()
            uid=hu.add(data)
            row={
                'id' : uid
            }
            self.response(row)
        except BaseError as e:
            self.gotoErrorPage(e.code)


