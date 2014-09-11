import mysql.connector
from mysql.connector import errorcode
import logging
import time
import hashlib
import base64


dbConfig = {
  'user': 'root',
  'password': '123456',
  'host': 'localhost',
  'database': 'JctOAuth',
  'raise_on_warnings': True,
}

unixTimestamp=str(int(time.time()))

print('Jct OAuth Server System\n')
appName=input('Input App Name: ')
appDescription=input('Input App Description: ')
m=hashlib.md5()

try:
    cnx = mysql.connector.connect(**dbConfig)
    cur = cnx.cursor()

    # 在数据库中保存APP名字,创建时间,当前的时间戳
    sql_insert='''insert into `tabApps`(name,description,cratetime,timestamp) 
    VALUES("%s","%s",now(),%s)''' % (appName,appDescription,unixTimestamp)
    
    cur.execute(sql_insert)
    # 取插入记录的id 
    rid=cur.lastrowid
    
    # 计算app_Id
    strRid=str(rid).encode(encoding='utf-8')
    #MD5
    m.update(strRid)  
    # 得到16位MD5 (32位MD5去掉两头的8位，取中间的16位)
    appId=m.hexdigest()[8:24]
    
    # 计算app_Secret
    strSecret='JCT'+appId+unixTimestamp+'APP'
    m.update(strSecret.encode(encoding='utf-8'))
    appSecret=m.hexdigest()
    
    #print('app id : %s\n'% appId)
    #print("app Secret : %s\n" % appSecret)
    
    sql_update='UPDATE `tabApps` SET app_key="%s",app_secret="%s" where id=%d' % (appId,appSecret,rid)
    #print(sql_update+'\n')
    cur.execute(sql_update)
    cnx.commit()
   
    print('App Name: %s \n' % appName )
    print('App Key:%s\n' % appId)
    print('App Secret:%s\n' % appSecret)
except mysql.connector.Error as err:
    print('Error: %d',err.msg)
    exit()
