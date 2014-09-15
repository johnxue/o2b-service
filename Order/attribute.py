import tornado.web
from dbMysql import dbMysql
import config
import json

class info(tornado.web.RequestHandler):
    
    def gotoErrorPage(self,error_code,es=None) :
        self.set_header('Access-Control-Allow-Origin','*')
        self.redirect('/o2b/v1.0.0/error/%d'% error_code )
        
    def post(self) :
        self.set_header('Access-Control-Allow-Origin','*')
        
    def options(self):
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,PATCH')
        self.set_header('Access-Control-Allow-Headers', 'app-key,authorization')
          
    def get(self):
        
        if self.request.headers.get('app-key')!=config.App_Key :
            # 601 : 数据库连接失败
            self.gotoErrorPage(601)
            return

        try :
            db=dbMysql(config.dbConfig)
        except :
            # 701 : 数据库连接失败
            self.gotoErrorPage(701)
            return
        
        row_Sort=None
        row_Status=None
        row_Type=None
        #1. 查询产品属性
        try :
            #1.1 查询付款方式；
            sqlSelect='SELECT description,code,comment FROM tbPayment order by sort desc'
            row_Payment=db.query(sqlSelect)
            #1.2. 查询配送方式；
            sqlSelect='SELECT description,code,comment FROM tbDelivery order by sort desc'
            row_Delivery=db.query(sqlSelect)
            #1.3. 获得时间段方式
            sqlSelect='SELECT description,code FROM vwQueryDate'
            row_Period=db.query(sqlSelect)
            
        except Exception as e:
             # 702 : SQL查询失败
            self.gotoErrorPage(702)
            return
        
        #2. 错误处理
        if (row_Payment is None) or (row_Delivery is None) :
            # '601' - 未被授权的应用
            self.gotoErrorPage(601)
            return
        
        #3. 打包成json object
        rows={
            'payment' : row_Payment,
            'delivery' : row_Delivery,
            'period':row_Period
        }
        
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Content-type','application/json;charset=utf-8');
        self.write(")]}',\n")
        self.write(json.dumps(rows,ensure_ascii=False))
        
        return
