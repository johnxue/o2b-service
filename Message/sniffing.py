from Framework.Base  import WebRequestHandler,BaseError
from Message import entity

class Handler(WebRequestHandler):
    # 用户查询圈子的所有话题例表
    def get(self):
        try :
            # 分页
            super().get(self)
            user   =self.getTokenToUser()
            msg     = entity.Message()
            countInfo = msg.sniffing(user)
            self.response(countInfo)
        except BaseError as e:
            self.gotoErrorPage(e.code)