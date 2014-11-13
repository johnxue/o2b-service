import mysql.connector
import mysql.connector.pooling 
import mysql.connector.cursor

from mysql.connector import errorcode
from Framework.Base  import BaseError

import logging,config

class Mysql(object):
    def __init__(self):
        if not hasattr(Mysql, 'pool'):  # 如果Mysql中无属性'pool'，则创建
            Mysql.create_pool(self,config.MysqlConfig)
        self._conn            = Mysql.pool.get_connection();
        self._cursor          = self._conn.cursor(buffered=True)
        self._conn.autocommit = True
    
    @staticmethod  
    def create_pool(self,config):  
        Mysql.pool = mysql.connector.pooling.MySQLConnectionPool(**config)


    def close(self):
        #关闭游标和数据库连接
        self._cursor.close()
        self._conn.close()
        pass
    
    def begin(self):
        self._conn.autocommit=False
        
    def commit(self):
        self._conn.commit()
        
    def rollback(self):
        self._conn.rollback()
    
    def count(self,table,params={},join='AND'):
        # 根据条件统计行数
        try :
            sql = 'SELECT COUNT(*) FROM `%s`' % table
            
            if params :
                where ,whereValues   = self.__contact_where(params)
                sqlWhere= ' WHERE '+where if where else ''
                sql+=sqlWhere
            
            #sql = self.__joinWhere(sql,params,join)
            cursor = self.__getCursor()
            cursor.execute(sql,tuple(whereValues))
            #cursor.execute(sql,tuple(params.values()))
            result = cursor.fetchone();
            return result[0] if result else 0
        except:
            raise BaseError(707)         

    def getToListByPk(self,table,criteria={},id=None,pk='id'):
        # 根据条件查找记录返回List
        if ('where' not in criteria) and (id is not None) :
            criteria['where']='`'+pk+'`="'+str(id)+'"'
        return self.__query(table,criteria,isDict=False)
    
    def getAllToList(self,table,criteria={},id=None,pk='id',join='AND'):
        # 根据条件查找记录返回List
        if ('where' not in criteria) and (id is not None) :
            criteria['where']='`'+pk+'`="'+str(id)+'"'
        return self.__query(table,criteria,all=True,isDict=False)

    def getToObjectByPk(self,table,criteria={},id=None,pk='id'):
        # 根据条件查找记录返回Object
        if ('where' not in criteria) and (id is not None) :
            criteria['where']='`'+pk+'`="'+str(id)+'"'
        return self.__query(table,criteria)

    def getAllToObject(self,table,criteria={},id=None,pk='id',join='AND'):
        # 根据条件查找记录返回Object
        if ('where' not in criteria) and (id is not None) :
            criteria['where']='`'+pk+'`="'+str(id)+'"'
        return self.__query(table,criteria,all=True)


    def insert(self,table,data,commit=True):
        # 新增一条记录
        try :
            
            ''' 
                从data中分离含用SQL函数的字字段到funData字典中,
                不含SQL函数的字段到newData
            '''            
            funData,newData=self.__split_expression(data)
            
            funFields='';funValues=''
            
            # 拼不含SQL函数的字段及值
            fields = ','.join('`'+k+'`' for k in newData.keys())
            values = ','.join(("%s", ) * len(newData))
            
            # 拼含SQL函数的字段及值            
            if funData :
                funFields = ','.join('`'+k+'`' for k in funData.keys()) 
                funValues =','.join( v for  v in funData.values())
                
            # 合并所有字段及值 
            fields += ','+funFields if funFields else ''
            values += ','+funValues if funValues else ''
            sql = 'INSERT INTO `%s` (%s) VALUES (%s)'%(table,fields,values)
            cursor = self.__getCursor()
            cursor.execute(sql,tuple(newData.values()))
            if commit : self.commit()
            insert_id = cursor.lastrowid
            return insert_id
        except:
            raise BaseError(703)
        
    def update(self,table,data,params={},join='AND',commit=True,lock=True):
        # 更新数据
        try :
            fields,values  = self.__contact_fields(data)
            if params :
                where ,whereValues   = self.__contact_where(params)
            
            values.extend(whereValues) if whereValues else values
            
            sqlWhere= ' WHERE '+where if where else ''

            cursor = self.__getCursor()
            
            if commit : self.begin()
            
            if lock :
                sqlSelect="SELECT %s From `%s` %s for update" % (','.join(tuple(list(params.keys()))),table,sqlWhere)
                cursor.execute(sqlSelect,tuple(whereValues))  # 加行锁
                
            sqlUpdate = "UPDATE `%s` SET %s "% (table,fields) + sqlWhere
            cursor.execute(sqlUpdate,tuple(values))

            if commit : self.commit()

            return cursor.rowcount
        except:
            raise BaseError(705)
        
    def updateByPk(self,table,data,id,pk='id',commit=True,lock=True):
        # 根据主键更新，默认是id为主键
        return self.update(table,data,{pk:id},commit=commit,lock=lock)
 
    
# 内部私有的方法 -------------------------------------------------------------------------------------
    def __get_connection(self):
        return self.pool.get_connection()
    
    def __getCursor(self):
        """获取游标"""
        if self.__cursor is None:
            self.__cursor = self.__conn.cursor()
        return self.__cursor

    def __joinWhere(self,sql,params,join):
        # 转换params为where连接语句
        if params:
            
            funParams={};newParams={};newWhere='';funWhere=''
            
            # 从params中分离含用SQL函数的字字段到Params字典中
            for (k,v) in params.items():
                if 'str' in str(type(v)) and '{{' == v[:2] and '}}'==v[-2:]  :
                    funParams[k]=v[2:-2]
                else:
                    newParams[k]=v

            # 拼 newParams 条件         
            keys,_keys = self.__tParams(newParams)
            newWhere = ' AND '.join(k+'='+_k for k,_k in zip(keys,_keys)) if join == 'AND' else ' OR '.join(k+'='+_k for k,_k in zip(keys,_keys))
            
            # 拼 funParams 条件
            if funParams :
                funWhere = ' AND '.join(k+'='+v for k,v in funParams.items()) if join == 'AND' else ' OR '.join(k+'='+v for k,v in funParams.items())
            
            # 拼最终的 where
            where=((newWhere+' AND ' if newWhere else '')+funWhere if funWhere else newWhere) if join=='AND' else ((newWhere+' OR ' if newWhere else '')+funWhere if funWhere else newWhere)
                
            #--------------------------------------
            #keys,_keys = self.__tParams(params)
            #where = ' AND '.join(k+'='+_k for k,_k in zip(keys,_keys)) if join == 'AND' else ' OR '.join(k+'='+_k for k,_k in zip(keys,_keys))
            sql+=' WHERE ' + where
        return sql
    
    def __tParams(self,params):
        keys = ['`'+k+'`'  if k[:2]!='{{' else k[2:-2] for k in params.keys()]
        _keys = ['%s' for k in params.keys()]
        return keys,_keys
    
    def __query(self,table,criteria,all=False,isDict=True,join='AND'):
        '''
           table    : 表名
           criteria : 查询条件dict
           all      : 是否返回所有数据，默认为False只返回一条数据,当为真是返回所有数据
           isDict   : 返回格式是否为字典，默认为True ，即字典否则为数组 
        
        '''
        try : 
            if all is not True:
                criteria['limit'] = 1  # 只输出一条
            sql,params = self.__contact_sql(table,criteria,join) #拼sql及params
            
            '''
            # 当Where为多个查询条件时，拼查询条件 key 的 valuse 值
            if 'where' in criteria and 'dict' in str(type(criteria['where'])) :
                params = criteria['where']
                #params = tuple(params.values())
                where ,whereValues   = self.__contact_where(params)
                sql+= ' WHERE '+where if where else ''
                params=tuple(whereValues)
            else :
                params = None
            '''
            #__contact_where(params,join='AND')
            cursor = self.__getCursor()
            cursor.execute(sql,params)
            
            rows = cursor.fetchall() if all else cursor.fetchone()
           
            if isDict :
                result = [dict(zip(cursor.column_names,row)) for row in rows] if all else dict(zip(cursor.column_names,rows)) if rows else {}
            else :
                result = [row for row in rows] if all else rows if rows else []
            return result
        except :
            raise BaseError(706)         
            
            
    def __contact_sql(self,table,criteria,join='AND'):
        sql = 'SELECT '
        if criteria and type(criteria) is dict:
            #select fields
            if 'select' in criteria:
                fields = criteria['select'].split(',')
                sql+= ','.join(field[2:-2] if '{{' == field[:2] and '}}'==field[-2:] else '`'+field+'`' for field in fields)
            else:
                sql+=' * '
            #table
            sql+=' FROM `%s`'%table
            #where
            if 'where' in criteria:
                if 'str' in str(type(criteria['where'])) :   # 当值为String时，即单一Key时
                    sql+=' WHERE '+ criteria['where']
                    whereValues=None
                else :                                       # 当值为dict时，即一组key时
                    params=criteria['where']
                    #sql+= self.__joinWhere('',params,join)
                    #sql+=self.__contact_where(params,join)
                    where ,whereValues   = self.__contact_where(params)
                    sql+= ' WHERE '+where if where else ''
                    #sql=sql % tuple(whereValues)
                    
            #group by
            if 'group' in criteria:
                sql+=' GROUP BY '+ criteria['group']
            #having
            if 'having' in criteria:
                sql+=' HAVING '+ criteria['having']
            #order by
            if 'order' in criteria:
                sql+=' ORDER BY '+ criteria['order']
            #limit
            if 'limit' in criteria:
                sql+=' LIMIT '+ str(criteria['limit'])
            #offset
            if 'offset' in criteria:
                sql+=' OFFSET '+ str(criteria['offset'])
        else:
            sql+=' * FROM `%s`'%table
            
        return sql,whereValues

    # 将字符串和表达式分离
    def __split_expression(self,data) :
        funData={};newData={};funFields=''
                                
        # 从data中移出含用SQL函数的字字段到funData字典中
        for (k,v) in data.items():
            if 'str' in str(type(v)) and '{{' == v[:2] and '}}'==v[-2:] :
                funData[k]=v[2:-2]
            else : newData[k]=v
        
        return (funData,newData)
        
        
    # 拼Update字段    
    def __contact_fields(self,data) :
    
        funData,newData=self.__split_expression(data)
        if funData :
            funFields = ','.join('`'+k+'`=%s'  % (v) for k,v in funData.items())
        fields = ','.join('`'+k+'`=%s' for k in newData.keys())
        
        # fields 与 funFields 合并
        if funData :
            fields = ','.join([fields,funFields]) if fields else funFields
            
        values = list(newData.values())
        
        return (fields,values)
    
    def __hasKeyword(self,key) :
        if 'in ('  in key : return True
        if 'like ' in key : return True
        if '>' in key : return True
        if '<' in key : return True
        return False
        
    # 拼Where条件
    def __contact_where(self,params,join='AND') :
        funParams,newParams=self.__split_expression(params)
        
        # 拼 newParams 条件
        keys,_keys = self.__tParams(newParams)
        newWhere = ' AND '.join(k+'='+_k for k,_k in zip(keys,_keys)) if join == 'AND' else ' OR '.join(k+'='+_k for k,_k in zip(keys,_keys))
        values = list(newParams.values())
    
        # 拼 funParams 条件
        funWhere = ' AND '.join('`'+k+'`'+ (' ' if self.__hasKeyword(v) else '=') +v for k,v in funParams.items()) if join == 'AND' else ' OR '.join('`'+k+'`'+(' ' if self.__hasKeyword(v) else '=')+v for k,v in funParams.items())

        # 拼最终的 where
        where=((newWhere+' AND ' if newWhere else '')+funWhere if funWhere else newWhere) if join=='AND' else ((newWhere+' OR ' if newWhere else '')+funWhere if funWhere else newWhere)
        return (where,values)
    
    
    def get_ids(self,list): #从getAllToList返回中提取id
        try:
            test=list[0][0]
            dimension=2
        except:
            dimension=1
            
        ids=[]
        if dimension>1 : 
            for i in range(len(list)) : ids.append(str(list[i][0]))
        else : 
            for i in range(len(list)) : ids.append(str(list[i]))
        
        return ','.join(ids)    
#-------------------------------------------------------------------------------------------------
class DB():
    
    def __init__(self,config):
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(**config)
            self.cnx=self.cur=None
        except mysql.connector.Error as err:
            # 这里需要记录操作日志
            logging.debug(err.msg)
            self.cnx=None
            raise BaseError(701) # 与数据库连接异常

    
    def open(self):
        try :
            self.__conn   = self.pool.get_connection();
            self.__cursor = self.__conn.cursor(buffered=True)
            self.__conn.autocommit=True
            self.cnx=self.__conn
            self.cur=self.__cursor
        except :
            raise BaseError(702) # 无法获得连接池
    
    def close(self):
        #关闭游标和数据库连接
        if self.__cursor is not None:
            self.__cursor.close()
        self.__conn.close()    

        
    def begin(self):
        self.__conn.autocommit=False
    
    def commit(self):
        self.__conn.commit()
        
    def rollback(self):
        self.__conn.rollback()
    
#---------------------------------------------------------------------------
    def findBySql(self,sql,params = {},limit = 0,join = 'AND',lock=False):
        """
            自定义sql语句查找
            limit = 是否需要返回多少行
            params = dict(field=value)
            join = 'AND | OR'
        """
        try :
            cursor = self.__getCursor()
            sql = self.__joinWhere(sql,params,join)
            cursor.execute(sql,tuple(params.values()))
            rows = cursor.fetchmany(size=limit) if limit > 0 else cursor.fetchall()
            result = [dict(zip(cursor.column_names,row)) for row in rows] if rows else None
            return result
        except:
            raise BaseError(706)
            
    
    def countBySql(self,sql,params = {},join = 'AND'):
        # 自定义sql 统计影响行数
        try:
            cursor = self.__getCursor()
            sql = self.__joinWhere(sql,params,join)
            cursor.execute(sql,tuple(params.values()))
            result = cursor.fetchone();
            return result[0] if result else 0
        except:
            raise BaseError(707)


    
    
    #def updateByPk(self,table,data,id,pk='id'):
    #    # 根据主键更新，默认是id为主键
    #    return self.updateByAttr(table,data,{pk:id})
    
    def deleteByAttr(self,table,params={},join='AND'):
        # 删除数据
        try :
            fields = ','.join('`'+k+'`=%s' for k in params.keys())
            sql = "DELETE FROM `%s` "% table
            sql = self.__joinWhere(sql,params,join)
            cursor = self.__getCursor()
            cursor.execute(sql,tuple(params.values()))
            self.__conn.commit()
            return cursor.rowcount
        except:
            raise BaseError(704)         
    
    def deleteByPk(self,table,id,pk='id'):
        # 根据主键删除，默认是id为主键
        return self.deleteByAttr(table,{pk:id})
    
    def findByAttr(self,table,criteria = {}):
        # 根据条件查找一条记录
        return self.__query(table,criteria)
    
    def findByPk(self,table,id,pk='id'):
        return self.findByAttr(table,{'where':'`'+pk+'`='+str(id)})
    
    def findAllByAttr(self,table,criteria={}):
        # 根据条件查找记录
        return self.__query(table,criteria,True)
    


    def exit(self,table,params={},join='AND'):
        # 判断是否存在
        return self.count(table,params,join) > 0

# 公共的方法 -------------------------------------------------------------------------------------
    def count(self,table,params={},join='AND'):
        # 根据条件统计行数
        try :
            sql = 'SELECT COUNT(*) FROM `%s`' % table
            
            if params :
                where ,whereValues   = self.__contact_where(params)
                sqlWhere= ' WHERE '+where if where else ''
                sql+=sqlWhere
            
            #sql = self.__joinWhere(sql,params,join)
            cursor = self.__getCursor()
            cursor.execute(sql,tuple(whereValues))
            #cursor.execute(sql,tuple(params.values()))
            result = cursor.fetchone();
            return result[0] if result else 0
        except:
            raise BaseError(707)         

    def getToListByPk(self,table,criteria={},id=None,pk='id'):
        # 根据条件查找记录返回List
        if ('where' not in criteria) and (id is not None) :
            criteria['where']='`'+pk+'`="'+str(id)+'"'
        return self.__query(table,criteria,isDict=False)
    
    def getAllToList(self,table,criteria={},id=None,pk='id',join='AND'):
        # 根据条件查找记录返回List
        if ('where' not in criteria) and (id is not None) :
            criteria['where']='`'+pk+'`="'+str(id)+'"'
        return self.__query(table,criteria,all=True,isDict=False)

    def getToObjectByPk(self,table,criteria={},id=None,pk='id'):
        # 根据条件查找记录返回Object
        if ('where' not in criteria) and (id is not None) :
            criteria['where']='`'+pk+'`="'+str(id)+'"'
        return self.__query(table,criteria)

    def getAllToObject(self,table,criteria={},id=None,pk='id',join='AND'):
        # 根据条件查找记录返回Object
        if ('where' not in criteria) and (id is not None) :
            criteria['where']='`'+pk+'`="'+str(id)+'"'
        return self.__query(table,criteria,all=True)


    def insert(self,table,data,commit=True):
        # 新增一条记录
        try :
            
            ''' 
                从data中分离含用SQL函数的字字段到funData字典中,
                不含SQL函数的字段到newData
            '''            
            funData,newData=self.__split_expression(data)
            
            funFields='';funValues=''
            
            # 拼不含SQL函数的字段及值
            fields = ','.join('`'+k+'`' for k in newData.keys())
            values = ','.join(("%s", ) * len(newData))
            
            # 拼含SQL函数的字段及值            
            if funData :
                funFields = ','.join('`'+k+'`' for k in funData.keys()) 
                funValues =','.join( v for  v in funData.values())
                
            # 合并所有字段及值 
            fields += ','+funFields if funFields else ''
            values += ','+funValues if funValues else ''
            sql = 'INSERT INTO `%s` (%s) VALUES (%s)'%(table,fields,values)
            cursor = self.__getCursor()
            cursor.execute(sql,tuple(newData.values()))
            if commit : self.commit()
            insert_id = cursor.lastrowid
            return insert_id
        except:
            raise BaseError(703)
        
    def update(self,table,data,params={},join='AND',commit=True,lock=True):
        # 更新数据
        try :
            fields,values  = self.__contact_fields(data)
            if params :
                where ,whereValues   = self.__contact_where(params)
            
            values.extend(whereValues) if whereValues else values
            
            sqlWhere= ' WHERE '+where if where else ''

            cursor = self.__getCursor()
            
            if commit : self.begin()
            
            if lock :
                sqlSelect="SELECT %s From `%s` %s for update" % (','.join(tuple(list(params.keys()))),table,sqlWhere)
                cursor.execute(sqlSelect,tuple(whereValues))  # 加行锁
                
            sqlUpdate = "UPDATE `%s` SET %s "% (table,fields) + sqlWhere
            cursor.execute(sqlUpdate,tuple(values))

            if commit : self.commit()

            return cursor.rowcount
        except:
            raise BaseError(705)
        
    def updateByPk(self,table,data,id,pk='id',commit=True,lock=True):
        # 根据主键更新，默认是id为主键
        return self.update(table,data,{pk:id},commit=commit,lock=lock)
 
    
# 内部私有的方法 -------------------------------------------------------------------------------------
    
    def __get_connection(self):
        return self.pool.get_connection()
    
    def __getCursor(self):
        """获取游标"""
        if self.__cursor is None:
            self.__cursor = self.__conn.cursor()
        return self.__cursor

    def __joinWhere(self,sql,params,join):
        # 转换params为where连接语句
        if params:
            
            funParams={};newParams={};newWhere='';funWhere=''
            
            # 从params中分离含用SQL函数的字字段到Params字典中
            for (k,v) in params.items():
                if 'str' in str(type(v)) and '{{' == v[:2] and '}}'==v[-2:]  :
                    funParams[k]=v[2:-2]
                else:
                    newParams[k]=v

            # 拼 newParams 条件         
            keys,_keys = self.__tParams(newParams)
            newWhere = ' AND '.join(k+'='+_k for k,_k in zip(keys,_keys)) if join == 'AND' else ' OR '.join(k+'='+_k for k,_k in zip(keys,_keys))
            
            # 拼 funParams 条件
            if funParams :
                funWhere = ' AND '.join(k+'='+v for k,v in funParams.items()) if join == 'AND' else ' OR '.join(k+'='+v for k,v in funParams.items())
            
            # 拼最终的 where
            where=((newWhere+' AND ' if newWhere else '')+funWhere if funWhere else newWhere) if join=='AND' else ((newWhere+' OR ' if newWhere else '')+funWhere if funWhere else newWhere)
                
            #--------------------------------------
            #keys,_keys = self.__tParams(params)
            #where = ' AND '.join(k+'='+_k for k,_k in zip(keys,_keys)) if join == 'AND' else ' OR '.join(k+'='+_k for k,_k in zip(keys,_keys))
            sql+=' WHERE ' + where
        return sql
    
    def __tParams(self,params):
        keys = ['`'+k+'`'  if k[:2]!='{{' else k[2:-2] for k in params.keys()]
        _keys = ['%s' for k in params.keys()]
        return keys,_keys
    
    def __query(self,table,criteria,all=False,isDict=True,join='AND'):
        '''
           table    : 表名
           criteria : 查询条件dict
           all      : 是否返回所有数据，默认为False只返回一条数据,当为真是返回所有数据
           isDict   : 返回格式是否为字典，默认为True ，即字典否则为数组 
        
        '''
        try : 
            if all is not True:
                criteria['limit'] = 1  # 只输出一条
            sql,params = self.__contact_sql(table,criteria,join) #拼sql及params
            
            '''
            # 当Where为多个查询条件时，拼查询条件 key 的 valuse 值
            if 'where' in criteria and 'dict' in str(type(criteria['where'])) :
                params = criteria['where']
                #params = tuple(params.values())
                where ,whereValues   = self.__contact_where(params)
                sql+= ' WHERE '+where if where else ''
                params=tuple(whereValues)
            else :
                params = None
            '''
            #__contact_where(params,join='AND')
            cursor = self.__getCursor()
            cursor.execute(sql,params)
            
            rows = cursor.fetchall() if all else cursor.fetchone()
           
            if isDict :
                result = [dict(zip(cursor.column_names,row)) for row in rows] if all else dict(zip(cursor.column_names,rows)) if rows else {}
            else :
                result = [row for row in rows] if all else rows if rows else []
            return result
        except :
            raise BaseError(706)         
            
            
    def __contact_sql(self,table,criteria,join='AND'):
        sql = 'SELECT '
        if criteria and type(criteria) is dict:
            #select fields
            if 'select' in criteria:
                fields = criteria['select'].split(',')
                sql+= ','.join(field.strip()[2:-2] if '{{' == field.strip()[:2] and '}}'==field.strip()[-2:] else '`'+field.strip()+'`' for field in fields)
            else:
                sql+=' * '
            #table
            sql+=' FROM `%s`'%table
            
            #where
            whereValues=None
            if 'where' in criteria:
                if 'str' in str(type(criteria['where'])) :   # 当值为String时，即单一Key时
                    sql+=' WHERE '+ criteria['where']
                else :                                       # 当值为dict时，即一组key时
                    params=criteria['where']
                    #sql+= self.__joinWhere('',params,join)
                    #sql+=self.__contact_where(params,join)
                    where ,whereValues   = self.__contact_where(params)
                    sql+= ' WHERE '+where if where else ''
                    #sql=sql % tuple(whereValues)
                    
            #group by
            if 'group' in criteria:
                sql+=' GROUP BY '+ criteria['group']
            #having
            if 'having' in criteria:
                sql+=' HAVING '+ criteria['having']
            #order by
            if 'order' in criteria:
                sql+=' ORDER BY '+ criteria['order']
            #limit
            if 'limit' in criteria:
                sql+=' LIMIT '+ str(criteria['limit'])
            #offset
            if 'offset' in criteria:
                sql+=' OFFSET '+ str(criteria['offset'])
        else:
            sql+=' * FROM `%s`'%table
            
        return sql,whereValues

    # 将字符串和表达式分离
    def __split_expression(self,data) :
        funData={};newData={};funFields=''
                                
        # 从data中移出含用SQL函数的字字段到funData字典中
        for (k,v) in data.items():
            if 'str' in str(type(v)) and '{{' == v[:2] and '}}'==v[-2:] :
                funData[k]=v[2:-2]
            else : newData[k]=v
        
        return (funData,newData)
        
        
    # 拼Update字段    
    def __contact_fields(self,data) :
    
        funData,newData=self.__split_expression(data)
        if funData :
            funFields = ','.join('`'+k+'`=%s'  % (v) for k,v in funData.items())
        fields = ','.join('`'+k+'`=%s' for k in newData.keys())
        
        # fields 与 funFields 合并
        if funData :
            fields = ','.join([fields,funFields]) if fields else funFields
            
        values = list(newData.values())
        
        return (fields,values)
    
    def __hasKeyword(self,key) :
        if 'in ('  in key : return True
        if 'like ' in key : return True
        if '>' in key : return True
        if '<' in key : return True
        return False
        
    # 拼Where条件
    def __contact_where(self,params,join='AND') :
        funParams,newParams=self.__split_expression(params)
        
        # 拼 newParams 条件
        keys,_keys = self.__tParams(newParams)
        newWhere = ' AND '.join(k+'='+_k for k,_k in zip(keys,_keys)) if join == 'AND' else ' OR '.join(k+'='+_k for k,_k in zip(keys,_keys))
        values = list(newParams.values())
    
        # 拼 funParams 条件
        funWhere = ' AND '.join('`'+k+'`'+ (' ' if self.__hasKeyword(v) else '=') +v for k,v in funParams.items()) if join == 'AND' else ' OR '.join('`'+k+'`'+(' ' if self.__hasKeyword(v) else '=')+v for k,v in funParams.items())

        # 拼最终的 where
        where=((newWhere+' AND ' if newWhere else '')+funWhere if funWhere else newWhere) if join=='AND' else ((newWhere+' OR ' if newWhere else '')+funWhere if funWhere else newWhere)
        return (where,values)
    
    
    def get_ids(self,list): #从getAllToList返回中提取id
        try:
            test=list[0][0]
            dimension=2
        except:
            dimension=1
            
        ids=[]
        if dimension>1 : 
            for i in range(len(list)) : ids.append(str(list[i][0]))
        else : 
            for i in range(len(list)) : ids.append(str(list[i]))
        
        return ','.join(ids)    