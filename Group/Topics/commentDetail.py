from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
#from Service import RichEditor
import re,json,os,datetime
from Framework.Base  import BaseError
import logging
import config


'''
查圈子的所有话题
# 关注
'''
class Handler(WebRequestHandler):
    # 查询圈子某一话题的回帖
    def get(self,tid=None):
        try:
            # 分页
            super().get(self)
            offset=int(self.get_argument("o",default=0))
            rowcount=int(self.get_argument("r",default=1000))
            offset=offset*rowcount
            user=self.getTokenToUser()
                
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
                'select' : 'rid,cid,tid,gid,user,nickname,header,contents,createTime,status_code,status',
                'where'  : 'FIND_IN_SET(cid,"%s")' % (cids)
            }
            listReplyContent = db.getAllToList('vwGTCReply',Select,tid)
            db.close()
            
            listCRContent=[{}]*intCountComment
           
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
