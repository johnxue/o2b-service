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
        
    def options(self,pcode):
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,PATCH')
        self.set_header('Access-Control-Allow-Headers', 'app-key,authorization')
        
        
    def get(self,pcode):
        
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
        
        row_BasicInfo={}
        row_HTML={}

        #1. 查询产品属性
        try :
            #1.1 查询产品基本信息；
            sqlSelect='''SELECT 
                           name,description,image,imageBanners,
                           starttime,endtime,status,supplierCode,supplierName,
                           currentPrice,originalPrice,
                           totalTopic,totalFollow,totalSold,`limit`,totalAmount,code,pid
                         FROM vwProductList where code="%s"
                      ''' %(pcode)
            row_basic=db.getToObject(sqlSelect)            
            
            #1.2. 查询产品详情；
            sqlSelect='SELECT description,html FROM tbProductDetail where code="%s" order by sort' % (pcode)
            rows_html=db.query(sqlSelect)
            
        except :
             # 702 : SQL查询失败
            self.gotoErrorPage(702)
            return
        
        #2. 错误处理
        if (row_basic is None) :
            # '801' - 未找到数据
            self.gotoErrorPage(801)
            return
        
        #3. 打包成json object
        rows={
            'basic' : row_basic,
            'html' : rows_html
        }
        
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Content-type','application/json;charset=utf-8');
        self.write(")]}',\n")
        self.write(json.dumps(rows,cls=DecimalEncoder,ensure_ascii=False))
        
        return
 
