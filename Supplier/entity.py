from Framework import dbRedis,dbMysql
from Framework.baseException import errorDic,BaseError
import msgpack,ujson,datetime


class supplier(object) :

    def __init__(self) :
        self.table        = 'tbSupplier'
        self.view         = 'vwSupplier'
        

    def add(self,data,db,commit=True):
        #加入到数据库
        id=db.insert(self.table,data,commit)
        if id<1 : raise BaseError(703) # SQL执行错误
        #data=db.getToListByPk(self.view,{},id)
        return id

    def update(self,id,data,db,commit=True):
        #数据更新到数据库
        rw=db.updateByPk(self.table,data,id)
        if rw<0 : raise BaseError(705) # SQL执行错误
        return rw

    def delete(self,ids,db):  #删除数据库表
        #1.数据更新到数据库
        rw=db.updateByPk(self.table,{'isDelete':'Y','updateTime':'{{now()}}'},'{{ in (%s)}}'%(ids),pk='pid') 
        if rw<0 : raise BaseError(705) # SQL执行错误
        return rw

    def getSupplierCodeList(self,db) :
        #管理状态；
        conditions = {
            'select' : 'id,code,companyName,pinyin'
        }
        rows_List = db.getAllToList(self.view,conditions)
        
        #错误处理
        if len(rows_List)==0:
            raise BaseError(802) # 无数据

        #3. 打包成json object
        rows={
            'supplier' : {
                'struct' : conditions['select'],
                'list'   : rows_List
            }
        }
        return rows
