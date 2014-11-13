from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
from AdSense import entity


class Handler(WebRequestHandler):
    #在广告管理中得到广告列表（多查询模式）
    def get(self):
        try :
            super().get(self)
            
            param = {
                # 分页控制
                'offset'        : int(self.get_argument("o",default='0')),
                'rowcount'      : int(self.get_argument("r",default='1000')),
                 # 排序方案
                 'order'        : self.get_argument("s",default='STARTTIME,DESC').upper(),
                 'ascOrDesc'    : self.get_argument("v",default= 'ASC').upper(),
                 # 关键字查询
                 'searchString' : self.get_argument("q",default=''),
                 # 按状态查询
                 'status'       : self.get_argument("st",default='').upper(),
                 # 按时间段查询
                 'startTime'    : self.get_argument("ts",default=''),
                 'endTime'      : self.get_argument("te",default=''),
                 # 过滤器查询
                 'filter'       : self.get_argument("ft",default='').upper()
            }
            
            db=self.openDB()
            ads=entity.adsense()
            rows=ads.getAllList(param,db)
            self.closeDB()
            self.response(rows)
            
        except BaseError as e:
            self.gotoErrorPage(e.code)
    
    # 增加新的广告 
    def post(self):
        try :
            super().get(self)
            userid=self.getTokenToUser()
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
                
            # 增加新广告代码
            try :
                data={
                    'contractNo' : objData['cn'],
                    'pid'        : objData['pid'],
                    'mode'       : objData['m'],
                    'channel'    : objData['c'],
                    'pageIndex'  : objData['n'],
                    'level'      : objData['l'],
                    'subIndex'   : objData['o'],
                    'startTime'  : objData['s'],
                    'endTime'    : objData['e']
                }
            except :
                raise BaseError(801) # 参数错误
            
            ads=entity.adsense()
            db=self.openDB()
            aid=ads.add(data,db)
            self.closeDB()
            row={
                'id' : aid
            }            
            self.response(row)
        except BaseError as e:
            self.gotoErrorPage(e.code)
    
    # 变更广告内容
    def put(self,id):
        try :
            super().get(self)
            userid=self.getTokenToUser()
            objData=self.getRequestData()
            data={}
            try :
                try :
                    data['contractNo']=objData['cn']
                except:
                    pass
                
                try :
                    data['pid']=objData['pid']
                except:
                    pass
                
                try :
                    data['mode']=objData['m']
                except:
                    pass
                
                try :
                    data['channel']=objData['c']
                except:
                    pass
                
                try :
                    data['pageIndex']=objData['n']
                except:
                    pass                
                
                try :
                    data['level']=objData['l']
                except:
                    pass
                
                try :
                    data['subIndex']=objData['o']
                except:
                    pass
                
                try :
                    data['startTime']=objData['s']
                except:
                    pass
                
                try :
                    data['endTime']=objData['e']
                except:
                    pass                 
            except :
                raise BaseError(801) # 参数错误
            
            ads=entity.adsense()
            db=self.openDB()
            aid=ads.update(data,id,db)
            self.closeDB()
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)
    
    # 修改/设置广告参数   
    def patch(self,id):
        try :
            super().get(self)
            userid=self.getTokenToUser()
            objData=self.getRequestData()
            data={
                'updateTime':'{{now()}}'
            }
            
            try :
                data['status']=objData['st'].upper()
                data['comments']=objData['cm']
            except :
                raise BaseError(801) # 参数错误
            
            ads=entity.adsense()
            db=self.openDB()
            aid=ads.update(data,id,db)
            self.closeDB()
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)
            
    # 删除广告
    def delete(self,id):
        try :
            super().get(self)
            userid=self.getTokenToUser()
           
            ads=entity.adsense()
            db=self.openDB()
            aid=ads.delete(id,db)
            self.closeDB()
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)       
            
            
    # 同步mysql与redis    
    def redisSync(self):
        ads=entity.adsense()
        db=self.openDB()
        list=ads.sync(db)
        self.closeDB()
        return list
        
        
    
