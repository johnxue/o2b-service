from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
import re,json,os,datetime
from Framework.Base  import BaseError
import logging
import config
from Service import uploadfile
from User import entity


'''
查热门贴子
# 关注
'''
class Handler(WebRequestHandler):
    # 用户查询圈子的所有话题例表
    def get(self):
        try :
            # 分页
            super().get(self)
            offset=int(self.get_argument("o",default=0))
            rowcount=int(self.get_argument("r",default=1000))
            
            offset=offset*rowcount
            objUser=self.objUserInfo
            user=objUser['user']            
    
            db=self.openDB()

            #1. 查询圈子的帖子
            hotTopicsSelect={
                'select' : "id,gid,user,nickname,{{CONCAT('%s/'}},{{header) as header}},topic,summary,createTime,viewCount,replyCount,isTop,isEssence,status_code,status" % (config.imageConfig['userheader']['url']),
                'where'  : "isNotHot is Null or upper(isNotHot)<>'Y'",
                'order'  : 'viewCount+replyCount desc',
                'limit' : '%s,%s' % (offset,rowcount)
            }
            
            #2. 查询符合条件的圈子总帖数
            countSelect={"":"{{isNotHot is Null or upper(isNotHot)<>'Y'}}"}
            
            intCountTopic=db.count('vwGroupTopics',countSelect)
            if intCountTopic==0 : raise BaseError(802) # 没有找到数据
            
            Topics_List = db.getAllToList('vwGroupTopics',hotTopicsSelect)
            db.close()
            
            #2. 错误处理
            if len(Topics_List)==0 : raise BaseError(802) # 没有找到数据
       
            #3. 打包成json object
            rows = {
                'count'  : intCountTopic,
                'struct' : 'id,gid,user,nickname,header,topic,summary,createTime,viewCount,replyCount,isTop,isEssence,status_code,status',
                'Topics' : Topics_List
            }
            self.response(rows)
        except BaseError as e:
            self.gotoErrorPage(e.code)
            
   