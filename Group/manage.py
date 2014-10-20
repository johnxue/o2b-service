from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
import config

class Handler(WebRequestHandler):
    def get(self,gid=None):  # 查询圈子的信息，前提是该圈子属于查询用户
        
        try :
            super().get(self)
            
            user=self.getTokenToUser()        
            # 分页
            offset=int(self.get_argument("o",default=0))
            rowcount=int(self.get_argument("r",default=1000))
            offset=offset*rowcount
            
            db=self.openDB()
            
            #1. 查询退换货单；
            conditions={
                'select' : 'id,name,description,membership，totalTopic',
                'where' : 'owner="%s"' % (user),
                'order' : 'id desc',
                'limit' : '%s,%s' % (offset,rowcount)
            }
            group_list=db.getAllToList('tbGroups',conditions)

            self.closeDB()
            
            #2. 错误处理
            if len(group_list)==0 :
                raise BaseError(802) # 没有找到数据                    
                
            #3. 打包成json object
            rows = {'myGroup' : group_list }
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
                    'name'         : objData["name"],                    # 圈子名称
                    'description'  : objData["desc"],                    # 圈子描述
                    'category'     : objData["cat"],                     # 圈子分类Code
                    'cratetime'    : self._now_time_,                    # 创建时间
                    'owner'        : user,                               # 圈子的所有者
                    'level'        : '100',                              # 初级
                    'totalTopic'   : 0,                                  # 总主题数
                    'totalReply'   : 0,                                  # 总回复数
                    'lastTime'     : self._now_time_,                    # 最后一次发帖时间
                    'active'       : 0,                                  # 活跃度
                    'status'       : 'W',                                # 状态：等待申批
                    'membership'   : 1  ,                                # 成员数为1
                    'isPrivate'    : 'Y' if objData["pwd"] else 'N',     # 如果有密码为Y否则为N
                    'password'     : objData["pwd"],                     # 私有密码
                    'isDelete'     : 'Y'
                }
            except :
                raise BaseError(801) # 参数错误
            
                
            
            db=self.openDB()
            db.begin()

            #1.1 将圈子信息插入 tbGroup;
            gid=db.insert('tbGroups',insertData,commit=False)
            
            if gid<0 : raise BaseError(702) # SQL操作失败
            
            #1.2 将用户信息插入到 tbGroupUser；
            guData = {
                'user'            : user,
                'groupid'         : gid,
                'joinTime'        : self._now_time_,
                'role'            : 'O',                 # O - 圈子所有者
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


    def patch(self):  # 管理圈子
        try :
            super().post(self)
            user=self.getTokenToUser()        
            objData=self.getRequestData()
            
            try :
                
                # 圈子信息
                objData={
                    'gid'       : int(objData["gid"]),               # 圈子id
                    'operation' : objData["opt"],                    # 圈子操作
                }
            except :
                raise BaseError(801) # 参数错误
            
            db=self.openDB()

            #1.3 将tbUser表中的lastGroup更新为新建圈子的id
            updateData={
                'status':objData['operation'], 
                'updateTime':self._now_time_,
                'updateUser':user
            }
            ur=db.update('tbGroup',updateData,updateData,{"id":objdata["gid"],"owner":user})      
            if ur<=0 :BaseError(802) # 没有数据找到
                
            self.closeDB()
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)
                        
    def delete(self):  # 解散圈子,须系统管理员
        pass
