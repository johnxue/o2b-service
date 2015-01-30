from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
#from Service import RichEditor
import re,json,os,datetime
from Framework.Base  import BaseError
import logging
import config
from User import entity

'''
查圈子的所有话题
# 关注
'''
class Handler(WebRequestHandler):
    # 新增对话题的评论    
    def post(self,cid):
        try:
            super().post(self)
            #user=self.getTokenToUser()
            objUser=self.objUserInfo
            user=objUser['user']
           
            objData=self.getRequestData()
            try:
                gid=objData['gid']
                tid=objData['tid']
                toUser=objData['touser']
                toNickname=objData['tonick']
                content=objData['content']
                status ='OK'
            except :
                raise BaseError(801) # 参数错误
            
           
            db=self.openDB()
            db.begin()
            
            #1.1 插入话题
            insertData={
                'gid'             : gid,
                'tid'             : tid,
                'cid'             : cid,
                'user'            : user,
                'nickname'        : objUser['nickname'],
                'toReplyUser'     : toUser,
                'toReplyNickname' : toNickname,
                'contents'        : content,
                'createTime'      : '{{now()}}',
                'isDelete'        : 'N',
                'status'          : status
            }
            rid=db.insert('tbGTCReply',insertData)
            
            db.close()
            if rid<0 : 
                # 插入失败后删除成功移动的文件
                oHuf.delFiles(oFileHtml['files'])
                raise BaseError(703) # SQL执行错误            

            rows={
                'rid' : rid
            }
         
            self.response(rows)
        except BaseError as e:
            self.gotoErrorPage(e.code) 
         
