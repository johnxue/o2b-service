from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
import config
from User import entity
from Framework import dbMysql



'''
圈子的用户管理 
1. 查询圈子的所有用户
2. 设置/去除管理员权限
3. 踢除用户
4. 对用户禁言
5. 审核验证用户
'''
class Handler(WebRequestHandler):
    
    # 查询圈子的所有用户
    def get(self,gid=None):  
        try :
            super().get(self)
            #user=self.getTokenToUser()
            objUser=self.objUserInfo
            user=objUser['user']                   
            
            status=self.get_argument("s",default='')
            role=self.get_argument("role",default='')
            

            # 分页
            offset=int(self.get_argument("o",default=0))
            rowcount=int(self.get_argument("r",default=1000))
            offset=offset*rowcount
                
            #db=self.openDB()
            #db =dbMysql.Mysql()
            db = self.openDB()
            
            #1. 判断用户是否为圈子的创建者或管理者，即核查管理权限
            SELECT={
                'select' : 'role',
                'where' : 'groupid=%s and user="%s"' % (gid,user)
            }
            user_role=db.getAllToObject('tbGroupUser',SELECT)
            if user_role[0]['role'] not in ['O','S'] :
                raise BaseError(604) # 未授权的访问
            
            #2. 查询圈子的用户数量条件
            countSelect={'gid':gid}
            
            
            #3. 得到圈子用户信息,不显示黑名单及待验证成员
            SELECT={
                'select' : 'id,user,role_code,role,joinTime,lasttime,totaltopic,status,verifyMessage',
                'where' : "gid=%s" % (gid,),
                'limit' : '%s,%s' % (offset,rowcount)
            }
            
            if role :
                SELECT['where']+=" and role_code in ('%s')" % (role,)
                countSelect['role_code']="{{in ('%s')}}" % (role,)
            else :
                SELECT['where']+=" and role_code in ('O','S','U')"
                countSelect['role_code']="{{in ('O','S','U')}}"
                
            if status : 
                SELECT['where']+=' and status="%s"' % (status,)
                countSelect['status']=status
            

                                    
            #3. 统计圈子的总用户数
            intCount=db.count('vwGroupUser',countSelect)
            if intCount==0 : raise BaseError(802) # 没有找到数据
            
            #4. 得到圈子用户
            user_list=db.getAllToList('vwGroupUser',SELECT)
            
            self.closeDB()
            #db.close()
            
            #2. 错误处理
            if len(user_list)==0 :
                raise BaseError(802) # 没有找到数据                    
                
            #3. 打包成json object
            rows = {
                'count'      : intCount,
                'GroupUsers' : user_list
            }
            
            self.response(rows)
             
        except BaseError as e:
            self.gotoErrorPage(e.code)


    def patch(self,gid):  # 设置或取消管理员权限/解除或设置禁言/审核用户/将用户拉黑
        try :
            super().post(self)
            #user=self.getTokenToUser()
            objUser=self.objUserInfo
            user=objUser['user']                   
            
            objData=self.getRequestData()
            guid=0
            
            try :
                updateData={
                    'lastTime'   : self._now_time_,
                    #'updateTime' : self._now_time_,
                    'lastUser'   : user
                }
                
                try :
                    guids = objData['guids']
                except :
                    guids = objData['vids']
                    updateData['verifyTime']=self._now_time_
                    
                try :
                    role = objData['role'].upper()
                except :
                    role = ''
                    
                try :
                    st = objData['st'].upper()
                except :
                    st = ''

                if len(guids)==0 : raise BaseError(801) # 参数错误
                
                # S|U|H|W  S-管理者 U-普通用户 H-黑名单用户 W-申请加入用户   
                if role : 
                    if role in ['S','U','H','W'] : updateData['role']   = role
                    else : raise BaseError(801) # 参数错误
                
                # OK|NO|KO  OK-正常 NO-禁止发言 KO-踢出，踢出用户同时做删除标志
                if st :
                    if st in 'OK,NO,KO,NP': 
                        updateData['status'] = st
                        if st=='NP':
                            updateData['role']   = 'W'
                            updateData['isDelete']='Y'       # 从圈子关系中删除
                            updateData['comment']='审核未通过' # 审核未通过原因
                                                   
                            #updateData['updateTime']=self._now_time_
                            #updateData['lastUser']=user      # 操作者为管理员                            
                            # 给用户发消息
                    else : raise BaseError(801) # 参数错误
                    
            except :
                raise BaseError(801) # 参数错误    
                        
            db=self.openDB()
            db.begin()
            ur=db.updateByPk('tbGroupUser',updateData,'{{ in (%s)}}'%(guids))      
            if ur<=0 :BaseError(802) # 没有数据找到
            
            if st=='NP' :  #审核未通过应该将圈子用户数-1
                # 更改 tbGroup.membership-1
                updateData={'membership':'{{if(membership>1,membership-1,1)}}'}
                db.updateByPk('tbGroups',updateData,gid,commit=False)                            
            
            db.commit()
            self.closeDB()
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)
                        
    def delete(self,gid):  # 踢除用户
        try :
            super().post(self)
            #user=self.getTokenToUser()
            objUser=self.objUserInfo
            user=objUser['user']                   
            
            objData=self.getRequestData()
            
            #KO-踢出，踢出用户同时做删除标志
            try :
                updateData={
                    'isDelete'   : 'Y',            # 从圈子关系中删除
                    'status'     : 'KO',           # 状态为踢出
                    'comment'    : objData['cmt'], # 踢出原因
                    'updateTime' : self._now_time_,
                    'lastUser'   : user            # 操作者为管理员
                }
                guid = objData['guid']
            except :
                raise BaseError(801) # 参数错误    
                        
            db=self.openDB()
            
            db.begin()
            
            ur=db.updateByPk('tbGroupUser',updateData,guid)      
            if ur<=0 :BaseError(802) # 没有数据找到
            
            # 更改 tbGroup.membership-1
            updateData={'membership':'{{if(membership>1,membership-1,1)}}'}            
            db.updateByPk('tbGroups',updateData,gid,commit=False) 
            
            db.commit()
            
                
            self.closeDB()
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)        
