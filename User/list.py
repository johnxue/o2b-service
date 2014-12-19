from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
from User import entity
import config

class Handler(WebRequestHandler):
 
    def get(self):
        try :
            super().get(self,userAuth=False)
            user     = self.get_argument("u",default='')
            nickname = self.get_argument("n",default='')
            
            result='N'
            r=0
            hu=entity.user()
            if    user     : r=hu.existsUsername(user)         
            elif  nickname : r=hu.existsNickname(nickname)         
            if r>0 : result='Y'
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
                       'user'       : objData['u'],
                       'password'   : objData['p'],
                       'nickname'   : objData['n'],
                       'header'     : config.Default_Header # 缺省的头像
                }
            except :
                raise BaseError(801) # 参数错误
            
            try :
                data['mobile']= objData['m']
            except :
                data['mobile']=''
                
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


