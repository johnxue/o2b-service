from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
import config
from easyOAuth.userinfo import Token

class Handler(WebRequestHandler):
    
    def delUserToken(self):
        token = self.getRequestHeader('Authorization')
        if token is not None  :
            try :
                myToken = Token(config.RedisConfig)
                s       = myToken.delUser(token) # 成功删除应返回成功受影响的记录数
            except:
                s = 0
        else :
            s = None
        return s
    

    def delete(self):  # 用户logout
        try :
            super().delete(self)
            
            token = self.getRequestHeader('Authorization')
            user  = self.getTokenToUser()
            
            r     = self.delUserToken()
        
            if r>0:
                strLogs = 'User:%s Token:%s [ Redisk 删除成功,r.delte()=%d ]' % (user,token,r)
            else :
                strLogs = 'User:%s Token:%s [ Redisk 删除失败,r.delete()=%d ]' % (user,token,r)
            
            if user is None :
                self.response()
                return

            db = self.openDB()
            
            # 更新 tbUser 表的用户最后一次登出时间
            db.updateByPk('tbUser',{'lastLogout':'{{now()}}'},user,pk='user')                        
            
            #2.2 插入 tbLogs 日志库；
            logsData = {
                'user': user,
                'level' : 'USE',
                'content': strLogs+' Logout 操作完成.',
                'createTime':'{{now()}}'
            }
            db.insert('tbLogs',logsData)
            
            self.closeDB()
            self.response()
            
        except BaseError as e:
            self.gotoErrorPage(e.code)
