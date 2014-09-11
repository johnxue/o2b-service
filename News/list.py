import tornado.web
from dbMysql import dbMysql
import config
import json
import decimal
import datetime

class DataTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


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
        
        offset=int(self.get_argument("o",default='0'))
        rowcount=int(self.get_argument("r",default='1000'))
        
        #1. 查询产品属性
        try :
            #1.1 查询产品属性；
            sqlSelect='SELECT id,title,author,source,summary,createTime,topLevel,CTR FROM tbNews order by topLevel desc,createtime desc limit %s,%s'
            rows_list=db.query(sqlSelect,(offset,rowcount))
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
        rows = {'news' : rows_list }
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Content-type','application/json;charset=utf-8');
        self.write(")]}',\n")
        self.write(json.dumps(rows,cls=DataTimeEncoder,ensure_ascii=False))
        
        return
 
