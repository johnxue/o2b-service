from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
from User import entity



class Handler(WebRequestHandler):
 
    def get(self):
        try :
            super().get(self,userAuth=False)
            user=self.get_argument("u",default='')
            result='N'
            if user : 
                hu=entity.user()
                r=hu.exists(user)         
                if r==1 : result='Y'
            self.response(result)
        except BaseError as e:
            self.gotoErrorPage(e.code)

        
    def post(self): 
        try :
            super().get(self,userAuth=False)
            #userid=self.getTokenToUser()
            objData=self.getRequestData()
            try :
                data={
                       'user'       : objData['user'],
                       'password'   : objData['pwd'],
                       'mobile'     : objData['mobile'],
                       'img_header' : objData['header']
                }
            except :
                raise BaseError(801) # 参数错误
            
            db=self.openDB()
            hu=entity.user()
            uid=hu.add(data,db)
            self.closeDB()            
            
            row={
                'id' : uid
            }
            self.response(row)
        except BaseError as e:
            self.gotoErrorPage(e.code)


