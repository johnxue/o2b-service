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
            
    # 设置新闻的状态         
    def patch(self,id):
        try :
            super().patch(self)
            db = self.openDB()
            
            objData=self.getRequestData()
            user=self.getTokenToUser()
            
            try:
                st=objData['st']
            except :
                raise BaseError(801) # 参数例表错误
                
            #1. 查询新闻详情；
            updateData = {
                'status' :st ,
                'updateTime' : '{{now()}}',
                'updateUser' : user
            }
            
            db=self.openDB()
            rw=db.updateByPk('tbNews',updateData,id)
            self.closeDB()
            
            if rw<0 : raise BaseError(803) # 修改数据失败

            self.response()
            
        except BaseError as e:
            self.gotoErrorPage(e.code)            
            
    # 删除新闻         
    def delete(self,id):
        try :
            super().delete(self)
            db = self.openDB()
            
            objData=self.getRequestData()
            user=self.getTokenToUser()
                
            #1. 查询新闻详情；
            updateData = {
                'status' :'UD' , #此状态应该根据用户的权限来判读 UD|AD
                'updateTime' : '{{now()}}',
                'updateUser' : user,
                'isDelete'   : 'Y'
            }
            
            db=self.openDB()
            #rw=db.update('tbNews',updateData,{'id':id,'user':user})
            rw=db.updateByPk('tbNews',updateData,id)
            self.closeDB()
            if rw<0 : raise BaseError(803) # 修改数据失败

            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)     
