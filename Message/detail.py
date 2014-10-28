from Framework.Base  import WebRequestHandler,BaseError
from Message import entity

class Handler(WebRequestHandler):
    # 得到消息实体
    def get(self,mid):
        try :
            super().get(self)
            user   =self.getTokenToUser()
            msg    = entity.Message()
            rows = msg.getMsg(mid)
            
            self.response(rows)
        except BaseError as e:
            self.gotoErrorPage(e.code)
            
