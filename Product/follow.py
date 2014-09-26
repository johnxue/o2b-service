from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

# 关注    
class hFollow(WebRequestHandler):
        
    # 加关注
    def post(self,code):
        try :
            super().post(self)
            user=self.getTokenToUser()
        
            db=self.openDB()
            db.begin()

            #1.1 插入到关注库 tbProductFollower；
            followerData = {
                'user'       : user,
                'pCode'      : code,
                'followtime' : '{{now()}}',
                'isDelete'   : 'N'
            }
            id = db.insert('tbProductFollower',followerData,commit=False)            
               
            if id < 0  :
                raise BaseError(702) # SQL 执行失败
            
            #1.2 更改tbUser.totalFollow+1,tbProdcutList.totalFollow+1
            updateData = { 'totalFollow':'{{totalFollow+1}}' }
            db.updateByPk('tbUser',updateData,user,pk='user',commit=False)
            db.updateByPk('tbProductList',updateData,code,pk='code',commit=False)

            db.commit()

            # 返回最后的关注数
            conditions = {
                'select' : 'code,totalFollow'
            }
            row_object = db.getToObjectByPk('tbProductList',conditions,code,pk='code')
            
            self.closeDB()
            
            self.response(row_object,201) # 201 创建对象成功
                        
        except BaseError as e:
            self.gotoErrorPage(e.code)
            
    
    # 取消关注
    def delete(self,code):
        try :
            super().delete(self)
            user=self.getTokenToUser()

            db=self.openDB()
            db.begin()
            
            #1.1 从关注库删除 tbProductFollower,这里有问题会产生表锁
            updateData = { 'isDelete':'Y' }
            whereData = {
                'user'  : user,
                'pcode' : code
            }
            db.update('tbProductFollower',updateData,whereData,commit=False)
            
            data={
                'totalFollow':'{{if(totalFollow>0,totalFollow-1,0)}}'
            }
            
            #1.2 更改tbUser.totalFollow-1
            db.updateByPk('tbUser',data,user,pk='user',commit=False)
            
            #1.3 更改tbProdcutList.totalFollow-1
            db.updateByPk('tbProductList',data,code,pk='code',commit=False)
            
          
            db.commit()
            
            # 返回最后的关注数
            returnData={
                'select' : 'code,totalFollow',
                'where'  : 'code="%s"' % (code)
            }
            
            row_object=db.getToObjectByPk('tbProductList',returnData,code,pk='code')
            
            self.closeDB()
            self.response(row_object)
                        
        except BaseError as e:
            self.gotoErrorPage(e.code)


    
    # 查询用户是否关注了某产品
    def get(self,code):
        try: 
            super().get(self)
            user=self.getTokenToUser()

            db=self.openDB()
            
            # 返回最后的关注数
            pl_object = db.getToObjectByPk('tbProductList',{'select':'code,totalFollow'},code,pk='code')            
            
            
            #1.1 查询 tbProductFollower 表；
            conditions = {
                'select' : 'user,pcode',
                'where'  : 'user="%s" and pcode="%s" and isDelete in ("N","",Null)' % (user,code)
            }
            pf_List = db.getAllToList('tbProductFollower',conditions)            
            
            if pf_List :
                pl_object[user]='YES'
            else :
                pl_object={}
                pl_object[user]='NO'

            self.closeDB()
            self.response(pl_object)
                        
        except BaseError as e:
            self.gotoErrorPage(e.code)
