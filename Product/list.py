from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

class info(WebRequestHandler):
    
    def get(self):
        
        try :
            #super().get(self)
            self._db_=None
            self.checkAppKey()        
            offset=int(self.get_argument("o",default='0'))
            rowcount=int(self.get_argument("r",default='1000'))
            offset=offset*rowcount
            sortName=self.get_argument("s",default='')
            sortValue=self.get_argument("v",default='')
            searchString=self.get_argument("q",default='')
        
            str_Order_by='';
            str_where='';
        
            if sortName == 'sort':
                str_Order_by='`%s` desc' % (sortValue)
        
            if sortName=='attribute' and sortValue!="ALL" :
                str_where='`statusCode`="%s"' % (sortValue)
            
            if sortName=='category' and sortValue!="0000" :
                str_where='`categoryCode`="%s"' % (sortValue) 
        
            sw=''
            if len(searchString)>0 :
                for word in searchString.split(' ') :
                    sw+='`name` like "%'+word+'%" or '
                
                searchString='%'+searchString.replace(' ','%')+'%'
                str_where=' %s `name` like "%s"' % (sw,searchString)
                 
            
            db=self.openDB()

            #1.1 查询产品；
            conditions = {
                #'select' : ('pid,code,categoryCode,name,image,createTime,updateTime,starttime,statusCode,status,'
                #            'totalTopic,totalFollow,totalSold,totalAmount'),
                'select' : ('pid,code,categoryCode,name,image,starttime,endTime,statusCode,status,'
                            'totalTopic,totalFollow,totalSold,totalAmount'),                
                'limit'  : '%s,%s' % (offset,rowcount)
            }
            if str_where    : conditions['where']=str_where
            if str_Order_by : conditions['order']=str_Order_by
            
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
