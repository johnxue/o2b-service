from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

class Handler(WebRequestHandler):

    def patch(self):  # 用户心跳
        
        try :
            super().patch(self)
            time=self.resetToken()
            if time<=0 :
                raise BaseError(601) #  未经授权的第三方应用
            self.response('%s' % (time),201) # 201 操作成功
            
        except BaseError as e:
            self.gotoErrorPage(e.code)
