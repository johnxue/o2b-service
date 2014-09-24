from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

class info(WebRequestHandler):

    def get(self): #功能: 查询用户关注列表返回产品信息
        try :
            super().get(self)
            user=self.getTokenToUser()
        
            offset=int(self.get_argument("o",default='0'))
            rowcount=int(self.get_argument("r",default='1000'))
            offset=offset*rowcount
            
            db=self.openDB()
            
            #1. 查询 tbProductFollower 表,并返回该用户所关注的产品code；
            conditions = {
                'select' : '{{distinct pcode}}',
                'where'  : 'user="%s" and isDelete<>"Y" or isDelete is Null' % (user)
            }
            pf_List = db.getAllToList('tbProductFollower',conditions)
            if len(pf_List)==0 :
                raise BaseError(802) # 未找到数据
            
            codes=db.get_ids(pf_List)  #取回产品code列表
            
            #2. 查询产品；
            conditions = {
                #'select' : ('pid,code,categoryCode,name,image,createTime,updateTime,starttime,statusCode,status,'
                #            'totalTopic,totalFollow,totalSold,totalAmount'),
                'select' : ('pid,code,categoryCode,name,image,starttime,endTime,statusCode,status,'
                            'totalTopic,totalFollow,totalSold,totalAmount'),                       
                'where'  : 'FIND_IN_SET(code,"%s")' % (codes),
                'order'  : 'pid desc',
                'limit'  : '%s,%s' % (offset,rowcount)
            }
            
            rows_list = db.getAllToList('vwProductList',conditions)  # 查询结果以List的方式返回  
            
            self.closeDB()
        
            #2. 错误处理
            if (len(rows_list)==0):
                raise BaseError(802) # 未找到数据
        
            #3. 打包成json object
            rows = {'rows' : rows_list }
            self.response(rows)
                        
        except BaseError as e:
            self.gotoErrorPage(e.code)
