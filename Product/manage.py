from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
from Product import entity


class Handler(WebRequestHandler):
    
    def get(self):
        
        try :
           
            super().get(self)
            objUser=self.objUserInfo
            user=objUser['user']
            
            status=self.get_argument("pms",default='')
            
            p=entity.product()
            db=self.openDB()
            
            # 当s=attribute 时获得产品管理状态
            if status.lower()=='attribute':
                rowData=p.getManageAttribute(db)
                self.closeDB()
                self.response(rowData)
                return
            
            param={}
            param['offset']       = int(self.get_argument("o",default='0'))
            param['rowcount']     = int(self.get_argument("r",default='1000'))
            param['sortName']     = self.get_argument("s",default='')
            param['sortValue']    = self.get_argument("v",default='')
            param['searchString'] = self.get_argument("q",default='')
            param['p_status']     = self.get_argument("mt",default='')
            param['user']         = user
            
            rows=p.getManageAllList(param,db)
            self.closeDB()            
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
                    'batchNo'       : objData['bn'],
                    'name'          : objData['name'],
                    'specification' : objData['spec'],
                    'description'   : objData['desc'],
                    'Image'         : objData['img'],
                    'imagelarge'    : objData['imgl'],
                    'imageBanners'  : objData['imgb'],
                    'imageSmall'    : objData['imgs'],
                    'supplierCode'  : objData['sc'],
                    'categoryCode'  : objData['cat'],
                    'statusCode'    : objData['st'],
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
            
            data['isOffline'] = 'N' #是否下线
            data['isDelete']  = 'N'  #是否删除
            data['createTime']='{{now()}}'
            data['createUserId']=user            
            
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
            rowData=p.changeProductList(data,db)
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
