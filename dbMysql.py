import mysql.connector
from mysql.connector import errorcode

class dbMysql():
    
    def __init__(self,config):
        try:
            self.cnx=mysql.connector.connect(**config)
            self.cur = self.cnx.cursor()
            #return self.cur
        except mysql.connector.Error as err:
            # 这里需要记录操作日志
            logging.debug(err.message)
            self.cnx=None
            
    def close(self):
        self.cur.close()
        self.cnx.close()
    
    def begin(self):
        self.cnx.autocommit=False
    
    def commit(self):
        self.cnx.commit()
        
    def rollback(self):
        self.cnx.rollback()
        
    def save(self,sql,params=None, multi=False):
        try:
            self.cur.execute(sql,params,multi)
            return self.cur.lastrowid
        except mysql.connector.cursor.errors as err:
            logging.debug(err.message)
            return -1
        
    def update(self,sql,params=None, multi=False):
        try:
            return self.cur.execute(sql,params,multi)
        except mysql.connector.cursor.errors as err:
            logging.debug(err.message)
            return None
        
    def delete(self,sql,params=None, multi=False):
        try:
            return self.cur.execute(sql,params,multi)
        except mysql.connector.cursor.errors as err:
            logging.debug(err.message)
            return None
        
    def query(self,sql,params=None, multi=False):
        try:
            self.cur.execute(sql,params,multi)
            return self.cur.fetchall()
        except mysql.connector.cursor.errors as err:
            logging.debug(err.message)
            return None
        #self.cursor.lastrowid
    
    def get(self,sql,params=None, multi=False):
        try:
            self.cur.execute(sql,params,multi)
            row=self.cur.fetchone()
            if row is not None:
                return row
            else:
                return None
        except mysql.connector.cursor.errors as err:
            logging.error(err.message)
            return None

    def getToList(self,sql,params=None, multi=False):
        return self.get(sql,params,multi)
    
        
    def getToObject(self,sql,params=None, multi=False):
        try:
            self.cur.execute(sql,params,multi)
            col=self.cur.column_names
            row=self.cur.fetchone()
            if row is not None :
                row=dict(zip(col,row))
            return row
        except mysql.connector.cursor.errors as err:
            logging.error(err.message)
            return None
