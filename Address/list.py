import tornado.web
from dbMysql import dbMysql
import config
import json
import decimal

class info(tornado.web.RequestHandler):
    
    def gotoErrorPage(self,error_code) :
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,PATCH')
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
        
        #country=self.get_argument("s",default='086')
        province=self.get_argument("p",default='')
        city=self.get_argument("c",default='')
        district=self.get_argument("d",default='')
        
        # 所有省
        if province+city+district=='':
            sqlSelect='SELECT provinceId,province FROM tbProvince order by provinceId'
            object_name='province'
        elif province!='' and city+district=='' :  # 某省下的所有市
            sqlSelect="SELECT cityId,city  FROM tbCity where father='%s' order by cityId" % (province)
            object_name='city'
        elif city!='' and province+district=='' : # 某省某市下的所有县或区
            sqlSelect="SELECT areaId,area FROM tbDistrict where father='%s' order by areaId" % (city)
            object_name='district'
        else :
            # 801 : 数据库连接失败
            self.gotoErrorPage(801)
            return
            
            
        #1. 查询行政区域Id
        try :
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
            # '802' - 未找到数据
            self.gotoErrorPage(802)
            return        
        
        #3. 打包成json object
        rows = {object_name : rows_list }
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Content-type','application/json;charset=utf-8');
        self.write(")]}',\n")
        self.write(json.dumps(rows,ensure_ascii=False))
        
        return
