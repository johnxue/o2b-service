from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
#from Service import RichEditor
import re,json,os,datetime
from Framework.Base  import BaseError
import logging
import config
from Service import uploadfile
from User import entity


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
            searchString=self.get_argument("q",default='')
            
            offset=offset*rowcount
            #user=self.getTokenToUser()
            objUser=self.objUserInfo
            user=objUser['user']            
    
            db=self.openDB()

            #1. 查询圈子的帖子
            topicsSelect={
                'select' : 'id,gid,user,nickname,header,topic,summary,createTime,viewCount,replyCount,isTop,isEssence,status_code,status',
                'where'  : "gid=%s" % (gid,),
                'limit' : '%s,%s' % (offset,rowcount)
            }
            
            #2. 查询符合条件的圈子总帖数
            countSelect={'gid':gid}
            
            #3. 增加搜索条件
            if len(searchString)>0 :
                topicsSelect['where']+=" and topic like '%"+searchString+"%'"
                countSelect['topic']="{{like '%"+searchString+"%'}}"
                
            intCountTopic=db.count('vwGroupTopics',countSelect)
            if intCountTopic==0 : raise BaseError(802) # 没有找到数据
            
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
            
    # 新增圈子话题    
    def post(self,gid):
        try:
            super().post(self)
            #user=self.getTokenToUser()
            objUser=self.getUserInfo()
            user=objUser['user']            
            objData=self.getRequestData()
            try:
                topic=objData['topic']
                summary = objData['summary']
                content=objData['content']
                imgFiles=objData['imgFiles']
                try :
                    status =objData['status']
                except :
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
            
            #1.1 插入话题
            insertData={
                'gid'        : gid,
                'user'       : user,
                'nickname'   : objUser['nickname'],
                'header'     : objUser['header'],
                'topic'      : topic,
                'summary'    : summary,
                'contents'   : oFileHtml['content'],
                'viewCount'  : 0,
                'replyCount' : 0,
                'createTime' : '{{now()}}',
                'isDelete'   : 'N',
                'isTop'      : 'N',
                'isEssence'  : 'N',
                'status'     : status
            }
            tid=db.insert('tbGroupTopics',insertData)
            db.close()
            if tid<0 : 
                # 插入失败后删除成功移动的文件
                oHuf.delFiles(oFileHtml['files'])
                raise BaseError(703) # SQL执行错误            

            rows={
                'tid' : tid
            }
            
            self.response(rows)
                
        except BaseError as e:
            self.gotoErrorPage(e.code)
            
            
    # 用户删除话题
    def delete(self,gid):
        try:
            super().post(self)
            #user=self.getTokenToUser()
            objUser=self.objUserInfo
            user=objUser['user']            
            
            objData = self.getRequestData()
            ids=objData['ids']
            db=self.openDB()
            
            #1.1 修改话题状态;
            updateData={
                'updateTime' : '{{now()}}',
                'status'     : 'UD',
                'isDelete'   : 'Y'
            }
            
            rowcount=db.updateByPk('tbGroupTopics',updateData,'{{ in (%s)}}'%(ids))
            db.close()
            
            if rowcount<0 :raise BaseError(802) # SQL执行没有成功,可能是user与tid不匹配，即用户只能删除自己的话题
                
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)
            

            
