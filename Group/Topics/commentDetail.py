from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
from Framework.Base  import BaseError

import re,json,os,datetime
import logging
import config
from Service import uploadfile
from User import entity

'''
查圈子的所有话题
# 关注
'''
class Handler(WebRequestHandler):
    # 查询圈子某一话题的回帖
    def get(self,tid):
        try:
            # 分页
            super().get(self)
            offset=int(self.get_argument("o",default=0))
            rowcount=int(self.get_argument("r",default=1000))
            offset=offset*rowcount
            #user=self.getTokenToUser()
            objUser=self.objUserInfo
            user=objUser['user']            
                
            db=self.openDB()
            
            #1. 查询圈子的总帖子数
            intCountComment=db.count('vwGTComment',{'tid':tid})
            if intCountComment==0 : raise BaseError(802) # 没有找到数据            
            
            #1. 查询圈子话题的评论（按时间顺序排例）
            Select={
                'select' : 'cid,tid,gid,user,nickname,header,contents,createTime,status_code,status',
                'where'  : "tid=%s" % (tid,),
                'limit' : '%s,%s' % (offset,rowcount)
            }
            
            listCommentContent = db.getAllToList('vwGTComment',Select,tid)
            
            if len(listCommentContent)==0 : raise BaseError(802) # 没有找到数据
            # 将cid单独取出来形成字符串 cids 
            cids=db.get_ids(listCommentContent)
            
            #2. 查询对评论的回复
            Select={
                'select' : 'rid,cid,tid,gid,user,nickname,header,toReplyUser,toReplyNickname,contents,createTime,status_code,status',
                'where'  : 'FIND_IN_SET(cid,"%s")' % (cids)
            }
            listReplyContent = db.getAllToList('vwGTCReply',Select,tid)
            db.close()
            
            listCRContent=[{}]*len(listCommentContent)
           
            for ci, comment in enumerate(listCommentContent):
                listReply=[]
                for ri,reply in enumerate(listReplyContent):
                    if reply[1]==comment[0] :  # cid相等,这里的效率有问题
                        listReply.append(reply)
                listCRContent[ci]={'comment':comment,'reply':listReply}
                
            
            #3. 打包成json object
            rows={
                'comments' : listCRContent,
                'count'    : intCountComment
            }
            self.response(rows)
        except BaseError as e:
            self.gotoErrorPage(e.code)
            
    
    # 新增对话题的评论    
    def post(self,tid):
        try:
            super().post(self)
            #user=self.getTokenToUser()
            objUser=self.objUserInfo
            user=objUser['user']
            
            objData=self.getRequestData()
            try:
                gid=objData['gid']
                content=objData['content']
                imgFiles=objData['imgFiles']
                status ='OK'
            except :
                raise BaseError(801) # 参数错误
            
            oFileHtml={
                'content':content,
                'files':None
            }            
            
            if imgFiles is not None :
                # 将临时图像文件移动到正式文件夹中,并更替Content里的图片链接为正式连接
                oHuf=uploadfile.uploadfile()
                # preImagesAndHtml 返回 {'files' : '含正式路径的文件名','content':'含正式URL的内容'}
                oFileHtml=oHuf.preImagesAndHtml(imgFiles,content,'group')     
                
            db=self.openDB()
            db.begin()
            
            #1.1 插入评论
            insertData={
                'gid'        : gid,
                'tid'        : tid,
                'user'       : user,
                'nickname'   : objUser['nickname'],
                'header'     : objUser['header'],
                'contents'   : oFileHtml['content'],
                'createTime' : '{{now()}}',
                'isDelete'   : 'N',
                'status'     : status
            }
            cid=db.insert('tbGTComment',insertData)
            db.close()
            if cid<0 : 
                # 插入失败后删除成功移动的文件
                oHuf.delFiles(oFileHtml['files'])
                raise BaseError(703) # SQL执行错误            

            rows={
                'cid' : cid
            }
            self.response(rows)
                
        except BaseError as e:
            self.gotoErrorPage(e.code) 
         
