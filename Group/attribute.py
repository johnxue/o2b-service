from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

class info(WebRequestHandler):

    def get(self):
        try :
            super().get(self)
            db=self.openDB()

            conditions = {
                'select' : 'description,code',
                'order'  : 'sort'
            }

            #1.2. 查询圈子分类；
            row_Category = db.getAllToList('tbGroupCategory',conditions)            

            #1.3. 查询圈子状态；
            conditions = {
                'select' : 'description,code',
                'order'  : 'sort'
            }
            row_Status = db.getAllToList('tbGroupStatus',conditions)
            
            self.closeDB()
        
            #2. 错误处理
            if len(row_Status)==0 or len(row_Category)==0 :
                raise BaseError(802) # 无数据
        
            #3. 打包成json object
            rows={
                'status' : row_Status,
                'category'  : row_Category,
            }
            self.response(rows)
            
        except BaseError as e:
            self.gotoErrorPage(e.code)