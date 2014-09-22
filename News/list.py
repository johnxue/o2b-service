from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

class info(WebRequestHandler):
    def get(self):
        try :
            super().get(self)
            
            offset   = int(self.get_argument("o",default='0'))
            rowcount = int(self.get_argument("r",default='1000'))
        
            db = self.openDB()
            
            #1.1 查询产品属性；
            conditions={
                'select' : 'id,title,author,source,summary,createTime,topLevel,CTR',
                'order'  : 'topLevel desc,createtime desc',
                'limit'  : '%s,%s' % (offset,rowcount)
            }
            rows_list = db.getAllToList('tbNews',conditions)

            self.closeDB()
            
            if len(rows_list)==0:
                raise BaseError(802) # 未找到数据
            
            #3. 打包成json object
            rows = {'news' : rows_list }
            self.response(rows)
            
        except BaseError as e:
            self.gotoErrorPage(e.code)
