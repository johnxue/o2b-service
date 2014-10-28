from Framework.Base  import WebRequestHandler,BaseError
from Message import entity

class Handler(WebRequestHandler):
    # 查询未读新消息
    def get(self,opt):
        try :
            # 分页
            super().get(self)
            offset   = int(self.get_argument("o",default=0))
            rowcount = int(self.get_argument("r",default=1000))
            
            offset = offset*rowcount
            user   =self.getTokenToUser()
            
            msg     = entity.Message()
            rows = msg.getList(user,opt,offset,rowcount)
            self.response(rows)
        except BaseError as e:
            self.gotoErrorPage(e.code)