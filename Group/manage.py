from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
import config

class Handler(WebRequestHandler):
    '''
        查询所有或指定用户的圈子
        当查询所有圈子时，只返回所有状态的圈子
        当查询指定用户的圈子时，将返回用户所创建的所有状态的圈子
    '''
    def get(self): 
        try :
            super().get(self)
            
            # 分页
            offset=int(self.get_argument("o",default=0))
            rowcount=int(self.get_argument("r",default=1000))
            user=self.get_argument("u",default='')
            status=(self.get_argument("s",default='')).upper()
            
            
            offset=offset*rowcount
            if user=='' : user=self.getTokenToUser()
            
                
            db=self.openDB()
            conditions={
                'select' : "gid,name,membership,totalTopic,status_code,status,isVerifyJoin,isPrivate,{{CONCAT('%s/'}},{{header) as header}},cat,owner,createtime" % (config.imageConfig['groupheader']['url']),
                'limit' : '%s,%s' % (offset,rowcount)
            }            
            
            keyName='AllGroups'
            where={ "{{1}}" : "1" }
            
                
            if user.lower()=='hot': # 热门圈子
                conditions['order'] = 'active desc'
                conditions['limit'] = 10
                keyName='HotGroups'
            elif user.lower()!='all' :  # 用户指定ID的圈子
                conditions['select']+= ',notice'
                conditions['where'] = 'owner="%s"' % (user,)
                where['owner']=user

                keyName=user + ' Groups'
 
            if status :
                try :
                    conditions['where'] = conditions['where'] + (' and ' if conditions['where'] else  '') + "status_code='%s'"%(status,)
                except :
                    conditions['where'] = "status_code='%s'"%(status,)
                where['status_code']=status
                    
            intCount=db.count('vwGroupList',where)
            if intCount==0 : raise BaseError(802) # 没有找到数据                   
            group_list=db.getAllToList('vwGroupList',conditions)
            self.closeDB()
            
            #2. 错误处理
            if len(group_list)==0 :
                raise BaseError(802) # 没有找到数据                    
                
            #3. 打包成json object
            rows = {
                'count' : intCount,           
                keyName : group_list
            }
            self.response(rows)
        except BaseError as e:
            self.gotoErrorPage(e.code)
            
    def patch(self):  # 设置圈子状态
        try :
            super().post(self)
            user=self.getTokenToUser()        
            objData=self.getRequestData()
            
            try:
                ids=objData['ids']
                #1.3 将tbUser表中的lastGroup更新为新建圈子的id
                updateData={
                    'status'       : objData["s"],                               # 圈子状态
                    'updateTime'   : '{{now()}}',
                    'updateUser'   : user
                }
            except :
                raise BaseError(801) # 参数错误
            
            if not updateData['status'] : raise BaseError(801) # 参数错误
                
            db=self.openDB()
            
            # 判断用户是否用管理员权限
            if user!=config.Administrator :
                SELECT={
                    'select' : 'role',
                    'where' : 'user="%s" and groupid=%s' % (user,gid),
                    'limit' : '1'
                }
                user_role=db.getAllToObject('tbGroupUser',SELECT)
                if len(user_role)==0 or user_role[0]['role'] not in 'OS':
                    raise BaseError(604) # 未授权的访问
            
            #ur=db.update('tbGroups',updateData,{"id":objData["gid"],"owner":user})
            ur=db.updateByPk('tbGroups',updateData,'{{ in (%s)}}'%(ids),pk='id')
            if ur<=0 :BaseError(802) # 没有数据找到
                
            self.closeDB()
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)

            
    def delete(self):  # 删除圈子
        try :
            super().post(self)
            user=self.getTokenToUser()        
            objData=self.getRequestData()
            
            try:
                ids=objData['ids']
                #1.3 将tbUser表中的lastGroup更新为新建圈子的id
                updateData={
                    'isDelete'       : 'Y',           # 删除圈子
                    'updateTime'   : '{{now()}}',
                    'updateUser'   : user
                }
            except :
                raise BaseError(801) # 参数错误
            
            db=self.openDB()
            
            # 判断用户是否用管理员权限
            if user!=config.Administrator :
                SELECT={
                    'select' : 'role',
                    'where' : 'user="%s" and groupid=%s' % (user,gid),
                    'limit' : '1'
                }
                user_role=db.getAllToObject('tbGroupUser',SELECT)
                if len(user_role)==0 or user_role[0]['role'] not in 'OS':
                    raise BaseError(604) # 未授权的访问
            
            ur=db.updateByPk('tbGroups',updateData,'{{ in (%s)}}'%(ids),pk='id')
            if ur<=0 :BaseError(802) # 没有数据找到
                
            self.closeDB()
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)
