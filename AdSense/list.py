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
        
    def options(self,channel,level):
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,PATCH')
        self.set_header('Access-Control-Allow-Headers', 'app-key,authorization')
        
    def get(self,channel,level):
        # channel - 网站频道
        # level - 该网站频道上的第几级页面
        
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
        
        #1. 查询广告属性
        try :
            #1.1 查询广告属性；
            sqlSelect='SELECT code,imageBanners FROM vwAdSenseList where channel="%s" and pageIndex=%s and level=1 order by subIndex' %(channel,level)
            rows_level_01=db.query(sqlSelect)
            sqlSelect='SELECT code,name,description,imagelarge,starttime,status,totalAmount,totalTopic,totalFollow FROM vwAdSenseList where channel="%s" and pageIndex=%s and level=2 order by subIndex' %(channel,level)
            rows_level_02=db.query(sqlSelect)
        except :
            # 702 : SQL查询失败
            self.gotoErrorPage(702)
            return
        
        #2. 错误处理
        if ((rows_level_01 is None) or (rows_level_02 is None)) :
            # '601' - 未被授权的应用
            self.gotoErrorPage(601)
            return
        
        #3. 错误处理
        if (len(rows_level_01)==0 and len(rows_level_02)==0):
            # '802' - 未找到数据
            self.gotoErrorPage(802)
            return        
        
        #3. 打包成json object
        rows = {
                'ads_level_01' : rows_level_01,
                'ads_level_02' : rows_level_02
                }
        #self.set_header('Authorization', 'Basic '+authcode)
        self.set_header('Access-Control-Allow-Origin','*')
        #self.set_header('Access-Control-Allow-Methods','*')
        self.set_header('Content-type','application/json;charset=utf-8');
        self.write(")]}',\n")
        self.write(json.dumps(rows,cls=DecimalEncoder,ensure_ascii=False))
        
        return
 
