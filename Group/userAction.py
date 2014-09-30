from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

# 关注    
class Handler(WebRequestHandler):
        
    # 加入圈子
    def post(self,groupid):
        try :
            super().post(self)
            user=self.getTokenToUser()
        
            db=self.openDB()
            db.begin()

            #1.1 插入到关注库 tbProductFollower；
            followerData = {
                'user'            : user,
                'groupid'         : groupid,
                'joinTime'        : self._now_time_,
                'role'            : 'U',                 # 普通用户
                'isDelete'        : 'N'
            }
            id = db.insert('tbGroupUser',followerData,commit=False)            
               
            if id < 0  :
                raise BaseError(702) # SQL 执行失败
            
            #1.2 更改 tbGroup.membership+1
            updateData = { 'membership':'{{membership+1}}' }
            db.updateByPk('tbGroup',updateData,gid,commit=False)

            db.commit()

            # 返回最后的圈子人数
            conditions = {
                'select' : 'id,name,membership'
            }
            row_object = db.getToObjectByPk('tbGroup',conditions,gorupid)
            
            self.closeDB()
            
            self.response(row_object,201) # 201 创建对象成功
                        
        except BaseError as e:
            self.gotoErrorPage(e.code)
            
    
    # 退出圈子
    def delete(self,groupid):
        try :
            super().delete(self)
            user=self.getTokenToUser()

            db=self.openDB()
            db.begin()
            
            #1.1 将 tbGroupUser.quitTime=当前时间 tbGroupUser.isDelete='Y'
            updateData = { 'quittime':self._now_time_,'isDelete':'Y' }
            whereData  = {'user':user , 'id':groupid }
            rc=db.update('tbProductFollower',updateData,whereData,commit=False,lock=False) #不加锁，规避表锁问题
            
            if rc<=0 :
                raise BaseError(802)  # 没有找到
                
            #1.2 更改 tbGroup.membership-1
            data={'membership':'{{if(membership>1,membership-1,1)}}'}            
            db.updateByPk('tbGroup',updateData,gid,commit=False)
            
            db.commit()
            
            # 返回最后的圈子人数
            conditions = {
                'select' : 'id,name,membership'
            }
            row_object = db.getToObjectByPk('tbGroup',conditions,gorupid)            
            
            self.closeDB()
            self.response(row_object)
                        
        except BaseError as e:
            self.gotoErrorPage(e.code)


    
    # 用户查询自己加入的圈子
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
