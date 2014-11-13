from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
from AdSense import entity

class info(WebRequestHandler):
    
    def get(self,channel,pageindex):
        # channel - 网站频道
        # level - 该网站频道上的第几级页面
        
        try :
            ads=entity.adsense()
            rows=ads.getAdSense(channel,pageindex)
            self.response(rows)
            
        except BaseError as e:
            self.gotoErrorPage(e.code)
    
    
        
    def get_fromDB(self,channel,level):
        db=self.openDB()
        
        #1. 查询广告属性；
        
        conditions={
            'select' : 'code,imageBanners',
            'order'  : 'subIndex',
            'where'  : {
                'channel':channel,
                'pageIndex':level,
                'level':'T00'
            }
        }
        rows_level_01=db.getAllToList('vwAdSense',conditions)            
        
        conditions={
            'select' : 'code,name,description,imagelarge,starttime,endtime,statusCode,status,totalTopic,totalFollow,totalSold,totalAmount',
            'order'  : 'subIndex',
            'where'  : {
                'channel':channel,
                'pageIndex':level,
                'level':'C00'
            }
        }
        
        rows_level_02=db.getAllToList('vwAdSense',conditions)            
        
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
    
    
    
