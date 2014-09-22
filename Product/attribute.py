from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

class info(WebRequestHandler):

    def get(self):
        try :
            super().get(self)
            db=self.openDB()

            #1.1 查询产品属性；
            conditions = {
                'select' : 'description,code',
                'order'  : 'sort'
            }
            row_Status = db.getAllToList('tbProductStatus',conditions)            

            #1.2. 查询产品分类；
            row_Type = db.getAllToList('tbProductCategory',conditions)            

            #1.3. 查询产品排序；
            conditions = {
                'select' : 'description,field',
                'order'  : 'sort'
            }
            row_Sort = db.getAllToList('tbProductOnline',conditions)
            
            self.closeDB()
        
            #2. 错误处理
            if len(row_Status)==0 or len(row_Type)==0 or len(row_Sort)==0:
                raise BaseError(802) # 无数据
        
            #3. 打包成json object
            rows={
                'attribute' : row_Status,
                'category'  : row_Type,
                'sort'      : row_Sort
            }
            self.response(rows)
            
        except BaseError as e:
            self.gotoErrorPage(e.code)