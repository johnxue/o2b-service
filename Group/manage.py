from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
import config

class info(WebRequestHandler):
    
    def get(self):  # 查询用户退换货信息
        
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
                'select' : ('id,swapOrderNo,orderNo,oid,pcode,pname,number,mode,description,'
                            'createTime,updateTime,status,comment'),
                'where' : 'user="%s"' % (user),
                'limit' : '%s,%s' % (offset,rowcount)
            }
            rows_list=db.getAllToList('vwReturns',conditions)

            self.closeDB()
            
            #2. 错误处理
            if len(rows_list)==0 :
                raise BaseError(802) # 没有找到数据                    
                
            #3. 打包成json object
            rows = {'swapOrder' : rows_list }
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
                    'isPrivate'    : 'Y' if objData["pwd"] else 'N',  # 如果有密码为Y否则为N
                    'password'     : objData["pwd"],                     # 私有密码
                    'isDelete'     : 'Y'
                }
            except :
                raise BaseError(801) # 参数错误
            
                
            #1.1 插入 tbOrder;
           
            
            db=self.openDB()
            db.begin()
            
            gid=db.insert('tbGroups',insertData,commit=False)
            
            if gid<0 : raise BaseError(702) # SQL操作失败
            
            #1.2 更改tbOrderList.status=310
            updateData={
                'lastGroupId':gid, 
                'updateTime':self._now_time_,
                'updateUser':user
            }
            db.updateByPk('tbUser',updateData,user,pk='user',commit=False)            

            db.commit()
            self.closeDB()
        
            #3. 打包成json object
            rows={
                "group"    : objData["name"],
                "id"       : gid
            }

            self.response(rows)
                        
        except BaseError as e:
            self.gotoErrorPage(e.code)
