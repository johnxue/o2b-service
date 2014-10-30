from Framework.Base  import WebRequestHandler,BaseError
from Message import entity

class Handler(WebRequestHandler):
    # 得到消息详情
    def get(self,mid):
        try :
            super().get(self)
            user   =self.getTokenToUser()
            msg    = entity.Message()
            rows = msg.getMsg(mid)
            self.response(rows)
        except BaseError as e:
            self.gotoErrorPage(e.code)
            

    # 删除指定消息
    def delete(self,mid):
        try :
            super().delete(self)
            user   =self.getTokenToUser()
            msg    = entity.Message()
            r = msg.remove(mid)
            if r==0 : raise BaseError(802) # 数据没有找到
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)
 