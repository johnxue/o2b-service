from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

# 关注    
class Handler(WebRequestHandler):
        
    # 加入圈子
    def post(self,groupid):
        try :
            super().post(self)
            user=self.getTokenToUser()
            objData=self.getRequestData()
            try :
                vm=objData['vm']
            except:
                vm=''
                
            st=objData['st'].upper()
            if (st=='WT' and vm=='') or (st not in ['WT','OK']):
                raise BaseError(801) # 参数错误
                
            db=self.openDB()
            db.begin()

            #1.1 插入到圈子用户库 tbGroupUser；
            guData = {
                'user'            : user,
                'groupid'         : groupid,
                'joinTime'        : self._now_time_,
                'role'            : 'W' if st=='WT' else 'U',                  # 普通用户
                'status'          : st, #ST有两种状态: WT-等待验证 OK-验证通过，可以发言
                'verifyMessage'   : vm,
                'isDelete'        : 'N'
            }
            
            id = db.insert('tbGroupUser',guData,commit=False)            
               
            if id < 0  :
                raise BaseError(702) # SQL 执行失败
            
            #1.2 更改 tbGroups.membership+1
            updateData = { 'membership':'{{membership+1}}' }
            db.updateByPk('tbGroups',updateData,groupid,commit=False)

            db.commit()

            # 返回最后的圈子人数
            conditions = {
                'select' : 'id,name,membership'
            }
            row_object = db.getToObjectByPk('tbGroups',conditions,groupid)
            
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
            
            #import pdb
            #pdb.set_trace()
            #1.1 将 tbGroupUser.quitTime=当前时间 tbGroupUser.isDelete='Y'
            updateData = { 'quittime':self._now_time_,'isDelete':'Y' }
            whereData  = {'user':user , 'groupid':groupid }
            rc=db.update('tbGroupUser',updateData,whereData,commit=False,lock=False) #不加锁，规避表锁问题
            
            if rc<=0 :
                raise BaseError(802)  # 没有找到
                
            #1.2 更改 tbGroup.membership-1
            updateData={'membership':'{{if(membership>1,membership-1,1)}}'}            
            db.updateByPk('tbGroups',updateData,groupid,commit=False)
            
            db.commit()
            
            # 返回最后的圈子人数
            conditions = {
                'select' : 'id,name,membership'
            }
            row_object = db.getToObjectByPk('tbGroups',conditions,groupid)            
            
            self.closeDB()
            self.response(row_object)
                        
        except BaseError as e:
            self.gotoErrorPage(e.code)


    
    # 用户查询默认用户在圈子中的权限
    def get(self,gid):
        try :
            super().get(self)
            user=self.getTokenToUser()
                   
            db=self.openDB()
            
            #1. 查询用户加入的所有圈子，返回圈子gid
            conditions={
                'select' : 'groupid,user,role,status',
                'where'  : "user='%s' and groupid=%s and (isDelete is Null or isDelete<>'Y')" % (user,gid)
            }
            user_Role = db.getToObjectByPk('tbGroupUser',conditions)
            self.closeDB()
            
            #2. 错误处理
            if len(user_Role)==0 :
                raise BaseError(802) # 没有找到数据                    
                
            #3. 打包成json object
            rows = {'UserGroupRole' : user_Role }
            self.response(rows)
        except BaseError as e:
            self.gotoErrorPage(e.code)
