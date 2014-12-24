from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
from Product import entity


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
        
            #where 用于统计
            where={ "{{1}}" : "1" }
        
            if sortName == 'sort':
                str_Order_by='`%s` desc' % (sortValue)
        
            if sortName=='attribute' and sortValue!="ALL" :
                str_where='`statusCode`="%s"' % (sortValue)
                where['statusCode']=sortValue
            
            if sortName=='category' and sortValue!="0000" :
                str_where='`categoryCode`="%s"' % (sortValue)
                where['categoryCode']=sortValue
        
            sw=''
            if len(searchString)>0 :
                for word in searchString.split(' ') :
                    sw+='`name` like "%'+word+'%" or '
                
                searchString='%'+searchString.replace(' ','%')+'%'
                str_where=' %s `name` like "%s"' % (sw,searchString)
                where["name"]="{{ like '%"+searchString+"' or "+sw+" 1 }}"
            
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
            
            intCountComment=db.count('vwProductList',where)
            if intCountComment==0 : raise BaseError(802) # 没有找到数据                   
            
            rows_list = db.getAllToList('vwProductList',conditions)  # 查询结果以List的方式返回  
            
            self.closeDB()
        
            #2. 错误处理
            if (len(rows_list)==0):
                raise BaseError(802) # 未找到数据
        
            #3. 打包成json object
            rows = {
                'struct':'pid,code,categoryCode,name,image,starttime,endTime,statusCode,status,'
                          'totalTopic,totalFollow,totalSold,totalAmount',             
                'rows' : rows_list,
                'count' : intCountComment
            }
            self.response(rows)
                        
        except BaseError as e:
            self.gotoErrorPage(e.code)
            
    def post(self):
        try :
            super().get(self)
            objUser=self.objUserInfo
            user=objUser['user']             
            objData=self.getRequestData()
            
            # 同步处理代码
            try :
                mode=objData['mode'].upper()
            except:
                mode=''
                                   
            if mode=='SYNC' :
                list=self.redisSync()
                self.response(list)
                return
                
            # 增加产品
            try :
                data={
                    'code'          : objData['c'],
                    'name'          : objData['name'],
                    'description'   : objData['desc'],
                    'Image'         : objData['img'],
                    'imagelarge'    : objData['imgl'],
                    'imageBanners'  : objData['imgb'],
                    #'imageSmall'    : objData['imgs'],
                    'supplierCode'  : objData['sc'],
                    'categoryCode'  : objData['cat'],
                    #'statusCode'    : objData['st'],
                    'startTime'     : objData['stm'],
                    'endTime'       : objData['etm'],
                    'currentPrice'  : objData['cp'],
                    'originalPrice' : objData['op'],
                    'totalAmount'   : objData['ta'],
                    'totalTopic'    : objData['tt'],
                    'totalFollow'   : objData['tf'],
                    'totalSold'     : objData['ts'],
                    'limit'         : objData['lmt'],
                }
            except :
                raise BaseError(801) # 参数错误
            
            try :
                data['batchNo'] = objData['bn']
            except :
                pass
            
            try :
                data['specification'] = objData['spec']
            except :
                pass            
                                    
            
            data['isOffline'] = 'N' #是否下线
            data['isDelete']  = 'N'  #是否删除
            data['createTime']='{{now()}}'
            data['createUserId']=user
            data['p_status']='WAIT'
            
            p=entity.product()
            db=self.openDB()
            #pid=p.addProductList(data,db)
            rowData=p.addProductList(data,db)
            self.closeDB()
            #row={
            #    objData['c'] : pid
            #}            
            self.response(rowData)
        except BaseError as e:
            self.gotoErrorPage(e.code)


    def put(self):
        try :
            super().get(self)
            objUser=self.objUserInfo
            user=objUser['user']             
            objData=self.getRequestData()
            
            # 修改产品
            lstData={
                'code'          : 'c',
                'batchNo'       : 'bn',
                'name'          : 'name',
                'specification' : 'spec',
                'description'   : 'desc',                
                'Image'         : 'img',
                'imagelarge'    : 'imgl',
                'imageBanners'  : 'imgb',
                'imageSmall'    : 'imgs',
                'supplierCode'  : 'sc',
                'categoryCode'  : 'cat',
                'statusCode'    : 'st',
                'startTime'     : 'stm',
                'endTime'       : 'etm',
                'currentPrice'  : 'cp',
                'originalPrice' : 'op',
                'totalAmount'   : 'ta',
                'totalTopic'    : 'tt',
                'totalFollow'   : 'tf',
                'totalSold'     : 'ts',
                'limit'         : 'lmt',
            }
            
            data={}
            
            for (k,v) in lstData.items():
                try:
                    data[k]=objData[v]
                except:
                    pass            
            
            if data is None or data=={} :
                raise BaseError(801) # 参数错误
            
            data['updateTime']='{{now()}}'
            data['updateUserId']=user            
            
            p=entity.product()
            db=self.openDB()
            rowData=p.updateProductList(data['code'],data,db)
            self.closeDB()
            self.response(rowData)
            #if row>0 :
            #    self.response()
            #else :
            #    raise BaseError(705) # 参数错误
                
        except BaseError as e:
            self.gotoErrorPage(e.code)
            
            
    # 批量删除产品
    def delete(self):
        try :
            super().get(self)
            objUser=self.objUserInfo
            user=objUser['user']
            objData=self.getRequestData()
            try:
                ids=objData[ids]
            except:
                raise BaseError(801) # 参数错误
            
            ads=entity.adsense()
            db=self.openDB()
            aid=ads.delete(ids,db)
            self.closeDB()
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)       
