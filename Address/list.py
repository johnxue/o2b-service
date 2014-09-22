from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

class info(WebRequestHandler):
    
    def get(self):
        try :
            super().get(self)

            #country=self.get_argument("s",default='086')
            province=self.get_argument("p",default='')
            city=self.get_argument("c",default='')
            district=self.get_argument("d",default='')
            
            
            if province+city+district=='':             # 所有省
                
                conditions={ 
                    'select' : 'provinceId,province',
                    'order'  : 'provinceId'
                }
                table,object_name=('tbProvince','province')
                
            elif province!='' and city+district=='' :  # 某省下的所有市
                
                conditions={
                    'select' : 'cityId,city',
                    'where'  : 'father="%s"' % (province),
                    'order'  : 'cityId'
                }
                table,object_name=('tbCity','city')
                
            elif city!='' and province+district=='' :  # 某省某市下的所有县或区
                
                conditions={
                    'select' : 'areaId,area',
                    'where'  : 'father="%s"' % (city),
                    'order'  : 'areaId',
                }
                table,object_name=('tbDistrict','district')
                
            else :
                raise BaseError(801) #801 : 参数错误

            db=self.openDB()
            rows_list=db.getAllToList(table,conditions)  # 查询结果以List的方式返回                   
            self.closeDB()
            
            if (len(rows_list)==0):
                raise BaseError(802) #802 未找到数据

            # 打包成json object
            rows = {object_name : rows_list }
            self.response(rows)
            
        except BaseError as e:
            self.gotoErrorPage(e.code)
