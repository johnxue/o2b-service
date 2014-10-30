from Framework.Base  import WebRequestHandler,BaseError
from Message import entity

class Handler(WebRequestHandler):
    # 用户查询圈子的所有话题例表
    def post(self,uid):
        try :
            # 分页
            super().get(self)
            user   =self.getTokenToUser()
            objData=self.getRequestData()
            
            try :
                messagePack={
                    'from'  : user,
                    'name'  : 'nickname',
                    'level' : 'U',
                    'title' : objData['title'],
                    'msg'   : objData['msg']
                }
            except :
                raise BaseError(801) # 参数错误
            
            msg     = entity.Message()
            countInfo = msg.send(uid,messagePack)
            if countInfo==1 : 
                self.response()
            else : 
                raise BaseError(818) # 发送消息失败
                
        except BaseError as e:
            self.gotoErrorPage(e.code)