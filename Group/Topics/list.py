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
    # 用户查询圈子的所有话题例表
    def get(self,gid=None):
        try :
            # 分页
            super().get(self)
            offset=int(self.get_argument("o",default=0))
            rowcount=int(self.get_argument("r",default=1000))
            offset=offset*rowcount
            user=self.getTokenToUser()
                
            db=self.openDB()
            
            #1. 查询圈子的总帖子数
            intCountTopic=db.count('vwGroupTopics',{'gid':gid})
            if intCountTopic==0 : raise BaseError(802) # 没有找到数据
            
            #2. 查询圈子的帖子
            topicsSelect={
                'select' : 'tid,gid,user,nickname,header,topic,{{left(contents}},{{200)}},createTime,viewCount,replyCount,isTop,isEssence,status_code,status',
                'where'  : "gid=%s" % (gid,),
                'limit' : '%s,%s' % (offset,rowcount)
            }
            Topics_List = db.getAllToList('vwGroupTopics',topicsSelect)
            db.close()
            
            #2. 错误处理
            if len(Topics_List)==0 : raise BaseError(802) # 没有找到数据
       
            #3. 打包成json object
            rows = {
                'gid'    : gid,
                'count'  : intCountTopic,
                'Topics' : Topics_List
            }
            self.response(rows)
        except BaseError as e:
            self.gotoErrorPage(e.code)
        
    def post(self,gid):
        try:
            super().post(self)
            user=self.getTokenToUser()
            objData=self.getRequestData()
            try:
                mode=objData['mode']
                type=objData['type']
                gid=objData['gid']
                tid=objData['tid']
                cid=objData['cid']
                rid=objData['rid']
                content=objData['content']
                lstImages=objData['imgURL']
            except :
                raise BaseError(801) # 参数错误
            
            if mode.upper()=='NEW' :
                db=self.openDB()
                db.begin()
                
                #1.1 插入 tbOrder;
                insertData={
                    'gid'        : gid,
                    'user'       : user,
                    'nickname'   : 'nickname',
                    'header'     : 'header',
                    'topic'      : topic,
                    'contents'   : contents,
                    'viewCount'  : 0,
                    'replyCount' : 0,
                    'createTime' : '{{now()}}',
                    'isDelete'   : 'N',
                    'isTop'      : 'N',
                    'isEssence'  : 'N',
                    'status'     : ''
                }
                topicId=db.insert('tbGroupTopics',insertData,commit=False)
                db.close()
                if topicId<0 :
                    raise BaseError(702) # SQL执行错误
                
                rows={
                    'gid' : gid,
                    'tid' : topicId
                }
                
                self.response(rows)
                
        except BaseError as e:
            self.gotoErrorPage(e.code)        
        
        
        
        
