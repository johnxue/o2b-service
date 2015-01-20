from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
import config
import Service.uploadfile
from Service.uploadfile import uploadfile

'''
圈子的用户管理 
1. 查询所有圈子或指定用户的圈子
2. 创建圈子
3. 圈子所有者设置圈子状态
4. 上传圈子头像
'''

class info(WebRequestHandler):
 
    '''
        查询所有或指定用户的圈子
        当查询所有圈子时，只返回状态为open和pause的圈子
        当查询指定用户的圈子时，将返回用户所创建的所有状态的圈子
    '''
    def get(self,gid=None): 
        try :
            super().get(self)
            
                   
            # 分页
            offset=int(self.get_argument("o",default=0))
            rowcount=int(self.get_argument("r",default=1000))
            user=self.get_argument("u",default='')
            gid=int(self.get_argument("g",default=0))
            
            offset=offset*rowcount
            if user=='' : user=self.getTokenToUser()
                
            db=self.openDB()
            conditions={
                'select' : "gid,name,cat,membership,totalTopic,status_code,status,isVerifyJoin,isPrivate,{{CONCAT('%s/'}},{{header) as header}}" % (config.imageConfig['groupheader']['url']),
                'where'  : "FIND_IN_SET(UPPER(status_code),'OPEN,PAUSE')>0",
                'limit' : '%s,%s' % (offset,rowcount)
            }            
            
            keyName='AllGroups'
            if user.lower()=='hot': # 热门圈子
                conditions['order'] = 'active desc'
                conditions['limit'] = 10
                keyName='HotGroups'
            elif user.lower()!='all' :  # 用户指定ID的圈子
                conditions['select']+= ',notice'
                #conditions['where'] = 'owner="%s" %s' % (user,' and gid=%d' % (gid,) if gid>0 else '' )
                if gid>0 :
                    conditions['where'] = 'gid=%d' % (gid,)
                else :
                    conditions['where'] = 'owner="%s"' % (user,)

                keyName='MyGroup' if gid>0 else 'MyGroups'
 
            group_list=db.getAllToList('vwGroupList',conditions)
            self.closeDB()
            
            #2. 错误处理
            if len(group_list)==0 :
                raise BaseError(802) # 没有找到数据                    
                
            #3. 打包成json object
            rows = {keyName : group_list }
            self.response(rows)
        except BaseError as e:
            self.gotoErrorPage(e.code)


    def post(self):  # 创建圈子
        try :
            super().post(self)
            user=self.getTokenToUser()        
        
            objData=self.getRequestData()
            
            try :
                # 圈子信息
                insertData={
                    'name'         : objData["name"],                              # 圈子名称
                    'category'     : objData["cat"],                               # 圈子分类Code
                    'createtime'    : self._now_time_,                              # 创建时间
                    'owner'        : user,                                         # 圈子的所有者
                    'level'        : '100',                                        # 初级
                    'totalTopic'   : 0,                                            # 总主题数
                    'totalReply'   : 0,                                            # 总回复数
                    'lastTime'     : self._now_time_,                              # 最后一次发帖时间
                    'active'       : 0,                                            # 活跃度
                    'status'       : 'WAIT',                                       # 状态：等待申批
                    'membership'   : 1  ,                                          # 成员数为1
                    'isPrivate'    : 'Y' if objData["cnt"].upper()=='Y'  else 'N', # 内容权限控制
                    'isVerifyJoin' : 'Y' if objData["join"].upper()=='Y' else 'N', # 加入权限控制
                    'headerImage'  : 'default_group_header.jpg',                   # 默认圈子头像                       
                    'isDelete'     : 'N'
                }
            except :
                raise BaseError(801) # 参数错误
            
            db=self.openDB()
            db.begin()

            #1.1 将圈子信息插入 tbGroups;
            gid=db.insert('tbGroups',insertData,commit=False)
            
            if gid<0 : raise BaseError(702) # SQL操作失败
            
            #1.2 将用户信息插入到 tbGroupUser；
            guData = {
                'user'            : user,
                'groupid'         : gid,
                'joinTime'        : self._now_time_,
                'role'            : 'O',         # O - 圈子所有者 A-圈子管理者 U-圈子普通用户
                'isDelete'        : 'N'
            }
            id = db.insert('tbGroupUser',guData,commit=False)

            ''' 
            以下代码可以废弃
            #1.3 将tbUser表中的lastGroup更新为新建圈子的id
            updateData={
                'lastGroupId':gid, 
                'updateTime':self._now_time_,
                'updateUser':user
            }
            db.updateByPk('tbUser',updateData,user,pk='user',commit=False)            
            '''
            
            db.commit()
            self.closeDB()
        
            #3. 打包成json object
            rows={
                "group"    : objData["name"],
                "id"       : gid
            }
            
            '''
            
            HMSET 
            
            
            '''
            self.response(rows)
                        
        except BaseError as e:
            self.gotoErrorPage(e.code)


    def put(self):  # 设置圈子状态
        try :
            super().post(self)
            user=self.getTokenToUser()        
            objData=self.getRequestData()
            
            try:
                gid=objData['gid']
                #1.3 将tbUser表中的lastGroup更新为新建圈子的id
                updateData={
                    'isPrivate'    : 'Y' if objData["cnt"].upper()=='Y'  else 'N', # 内容权限控制, 
                    'isVerifyJoin' : 'Y' if objData["join"].upper()=='Y' else 'N', # 加入权限控制
                    'notice'       : objData["ntc"],                               # 圈子公告
                    'updateTime'   : self._now_time_,
                    'updateUser'   : user
                }
            except :
                raise BaseError(801) # 参数错误
                
            db=self.openDB()
            
            # 判断用户是否用管理员权限
            SELECT={
                'select' : 'role',
                'where' : 'user="%s" and groupid=%s' % (user,gid),
                'limit' : '1'
            }
            user_role=db.getAllToObject('tbGroupUser',SELECT)
            if len(user_role)==0 or user_role[0]['role'] not in 'OS':
                raise BaseError(604) # 未授权的访问
            
            #ur=db.update('tbGroups',updateData,{"id":objData["gid"],"owner":user})
            ur=db.updateByPk('tbGroups',updateData,gid)
            if ur<=0 :BaseError(802) # 没有数据找到
                
            self.closeDB()
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)
    
    # 上传圈子头像
    def patch(self):
        try:
            super().patch(self)
            user=self.getTokenToUser()
            objData=self.getRequestArguments()
            if objData=={} :
                raise BaseError(801) # 参数错误
            
            gid    =objData['gid']   # 圈子id
              
            # 看是HTML传过来的 files  是否含有 picture
            if self.request.files == {} or 'upfile' not in self.request.files :
                raise BaseError(801) # 参数错误
            
            objData={
                'type'    :'groupheader',
                'groupid' : gid,
                'files'   : self.request.files['upfile']
            }
            
            img=uploadfile()
            info=img.uploadImages(objData)
            
            updateData={
                'headerImage'  : info["filename"],
                'updateTime'   : self._now_time_,
                'updateUser'   : user
            }            
            
            db=self.openDB()
            ur=db.updateByPk('tbGroups',updateData,gid)
            if ur<=0 :BaseError(802) # 没有数据找到
            self.closeDB()
            rspData={
                "state": "SUCCESS",
                "url": info['url']+'/'+info['filename'],
                "filename": info['filename']
            }                           
            
            self.response(rspData)            
        except BaseError as e:
            self.gotoErrorPage(e.code)
         
        
    def delete(self):  # 解散圈子,须系统管理员
        pass
