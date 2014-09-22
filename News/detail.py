from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

class info(WebRequestHandler):
    def get(self,id):
        try :
            super().get(self)

            db = self.openDB()            

            #1. 查询新闻详情；
            conditions = {
                'select' : 'id,title,author,source,htmlContent,createTime,CTR' 
            }
            row = db.getToObjectByPk('tbNews',conditions,id)

            self.closeDB()
            
            #2. 错误处理
            if len(row)==0 :
                raise BaseError(802) # 未找到数据

            self.response(row)
            
        except BaseError as e:
            self.gotoErrorPage(e.code)
