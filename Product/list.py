import tornado.web
from dbMysql import dbMysql
import config
import json
import decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


class info(tornado.web.RequestHandler):
    
    def gotoErrorPage(self,error_code) :
        self.set_header('Access-Control-Allow-Origin','*')
        self.redirect('/o2b/v1.0.0/error/%d'% error_code )
        
    def options(self):
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,PATCH')
        self.set_header('Access-Control-Allow-Headers', 'app-key,authorization')
        
    def get(self):
        
        if self.request.headers.get('app-key')!=config.App_Key :
            # 601 : 未经授权的第三方应用
            self.gotoErrorPage(601)
            return
        
        try :
            db=dbMysql(config.dbConfig)
        except :
            # 701 : 数据库连接失败
            self.gotoErrorPage(701)
            return
        
        offset=self.get_argument("o",default='0')
        rowcount=self.get_argument("r",default='1000')
        sortName=self.get_argument("s",default='')
        sortValue=self.get_argument("v",default='')
        searchString=self.get_argument("q",default='')
        
        str_Order_by='';
        str_where='';
        
        if sortName=='sort':
            str_Order_by='order by %s desc' % (sortValue)
        
        if sortName=='attribute' and sortValue!="ALL" :
            str_where='where statusCode="%s"' % (sortValue)
            
        if sortName=='category' and sortValue!="0000" :
            str_where='where categoryCode="%s"' % (sortValue) 
        
        sw=''
        if len(searchString)>0 :
            for word in searchString.split(' ') :
                sw+='name like "%'+word+'%" or '
            
            searchString='%'+searchString.replace(' ','%')+'%'
            #str_where='where name like "%s" 1' % (searchString)
            str_where='where %s name like "%s"' % (sw,searchString)
             
            
        #1. 查询产品属性
        try :
            #1.1 查询产品属性；
            sqlSelect='SELECT pid,code,categoryCode,name,image,createTime,updateTime,starttime,statusCode,status,totalTopic,totalFollow,totalSold,totalAmount FROM vwProductList %s %s limit %s,%s' %(str_where,str_Order_by,offset,rowcount)
            rows_list=db.query(sqlSelect)
        except :
             # 702 : SQL查询失败
            self.gotoErrorPage(702)
            return
        
        #2. 错误处理
        if (rows_list is None):
            # '601' - 未被授权的应用
            self.gotoErrorPage(601)
            return
        
        #3. 错误处理
        if (len(rows_list)==0):
            # '801' - 未找到数据
            self.gotoErrorPage(801)
            return        
        
        #3. 打包成json object
        rows = {'rows' : rows_list }
        #self.set_header('Authorization', 'Basic '+authcode)
        self.set_header('Access-Control-Allow-Origin','*')
        #self.set_header('Access-Control-Allow-Methods','*')
        self.set_header('Content-type','application/json;charset=utf-8');
        self.write(")]}',\n")
        self.write(json.dumps(rows,cls=DecimalEncoder,ensure_ascii=False))
        
        return
 

