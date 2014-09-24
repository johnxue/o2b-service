from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

class info(WebRequestHandler):
    
    def get(self,channel,level):
        # channel - 网站频道
        # level - 该网站频道上的第几级页面
        try :
            db=self.openDB()
            
            #1. 查询广告属性；
            
            conditions={
                'select' : 'code,imageBanners',
                'order'  : 'subIndex',
                'where'  : {
                    'channel':channel,
                    'pageIndex':level,
                    'level':'1'
                }
            }
            rows_level_01=db.getAllToList('vwAdSenseList',conditions)            
            
            conditions={
                'select' : 'code,name,description,imagelarge,starttime,endtime,statusCode,status,totalTopic,totalFollow,totalSold,totalAmount',
                'order'  : 'subIndex',
                'where'  : {
                    'channel':channel,
                    'pageIndex':level,
                    'level':'2'
                }
            }
            
            rows_level_02=db.getAllToList('vwAdSenseList',conditions)            
            
            self.closeDB()
        
            #2. 错误处理
            if (len(rows_level_01)==0 and len(rows_level_02)==0):
                raise BaseError(802) #802 未找到数据
        
            #3. 打包成json object
            rows = {
                'ads_level_01' : rows_level_01,
                'ads_level_02' : rows_level_02
            }
            
            self.response(rows)
            
        except BaseError as e:
            self.gotoErrorPage(e.code)
