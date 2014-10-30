from Framework.Base  import WebRequestHandler,BaseError
from Message import entity

class Handler(WebRequestHandler):
    # 查询消息
    def get(self):
        try :
            # 分页
            super().get(self)
            user   =self.getTokenToUser()
            
            offset   = int(self.get_argument("o",default=0))
            rowcount = int(self.get_argument("r",default=1000))
            status=self.get_argument("s",default='UNREAD').upper()
            
            if status not in ['UNREAD','READ'] :
                raise BaseError(801) # 参数错误

            offset = offset*rowcount

            msg     = entity.Message()
            rows = msg.getList(user,status,offset,rowcount)
            if rows['msg_list_'+status]==[]:
                raise BaseError(802) # 没有找到数据
            self.response(rows)
        except BaseError as e:
            self.gotoErrorPage(e.code)
            
            
    # 发消息        
    def post(self):
        try :
            # 分页
            super().post(self)
            user   =self.getTokenToUser()
            objData=self.getRequestData()
            
            try :
                toUser=objData['to']
                messagePack={
                    'from'  : user,
                    'name'  : 'nickname',
                    'level' : 'U',
                    'title' : objData['title'],
                    'msg'   : objData['msg']
                }
            except :
                raise BaseError(801) # 参数错误
            
            msg     = entity.Message()
            countInfo = msg.send(toUser,messagePack)
            if countInfo==1 : 
                self.response()
            else : 
                raise BaseError(818) # 发送消息失败
            
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)

    # 删除指定消息
    def delete(self):
        try :
            super().delete(self)
            user   =self.getTokenToUser()
            objData=self.getRequestData()
            try:
                ids=objData['ids']
            except:
                raise BaseError(801) # 参数错误
                
            msg    = entity.Message()
            r = msg.remove(ids)
            if r==0 : raise BaseError(802) # 数据没有找到
            row={
                'count':r
            }
            self.response(row)
        except BaseError as e:
            self.gotoErrorPage(e.code)