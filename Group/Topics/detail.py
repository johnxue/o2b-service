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
    # 用户查询圈子的某一个话题具体内容
    def get(self,tid):
        try :
            super().get(self)
            
            # 分页
            offset=int(self.get_argument("o",default=0))
            rowcount=int(self.get_argument("r",default=1000))
            offset=offset*rowcount
            #user=self.getTokenToUser()
            objUser=self.objUserInfo
            user=objUser['user']            
                
            db=self.openDB()
            
            #1. 查询圈子的帖子
            Select={
                'select' : 'id,gid,user,nickname,header,topic,contents,createTime,viewCount,replyCount,isTop,isEssence,status_code,status',
                'where'  : "id=%s" % (tid,)
            }
            objTopicsContent = db.getToObjectByPk('vwGroupTopics',Select,tid)
            db.close()
            
            if len(objTopicsContent)==0 : raise BaseError(802) # 没有找到数据
            
            self.response(objTopicsContent)
        except BaseError as e:
            self.gotoErrorPage(e.code)
            
    # 用户修改话题
    def put(self,tid):
        try:
            super().post(self)
            #user=self.getTokenToUser()
            objUser=self.objUserInfo
            user=objUser['user']            
            objData=self.getRequestData()
            try:
                try :
                    topic=objData['topic']
                except:
                    topic=None
                
                try :
                    summary = objData['summary']
                except :
                    summary=None
                 
                try :  
                    content=objData['content']
                except :
                    content=None
                try :
                    imgFiles=objData['imgFiles']
                except :
                    imgFiles=None
                try :
                    removeImgFiles=objData['rImgFiles']
                except :
                    removeImgFiles=None
                
                try :
                    status =objData['status']
                except :
                    status =None          
            except :
                raise BaseError(801) # 参数错误
            
            oFileHtml={
                'content':content,
                'files':None
            }
            
            oHuf=uploadfile.uploadfile()
            
            if imgFiles is not None :
                # 将临时图像文件移动到正式文件夹中,并更替Content里的图片链接为正式连接
                # preImagesAndHtml 返回 {'files' : '含正式路径的文件名','content':'含正式URL的内容'}
                oFileHtml=oHuf.preImagesAndHtml(imgFiles,content,'group')
            
            db=self.openDB()
            
            #1.1 修改话题;
            updateData={
                'nickname'   : objUser['nickname'],
                'header'     : objUser['header'],
                'updateTime' : '{{now()}}'
            }
            
            # 如果内容为None即不修改
            if topic   is not None : updateData['topic']    = topic
            if content is not None : updateData['contents'] = oFileHtml['content']
            if status  is not None : updateData['status']   = status
            if summary is not None : updateData['summary']  = summary
                
            rowcount=db.update('tbGroupTopics',updateData,{'id':tid,'user':user}) 
            db.close()
            
            if rowcount<0 :
                # 插入失败后删除成功移动的文件
                oHuf.delFiles(oFileHtml['files'])              
                raise BaseError(802) # SQL执行没有成功,可能是user与tid不匹配，即用户只能删除自己的话题
            
            if removeImgFiles is not None :
                # 插入失败后删除成功移动的文件
                oHuf.delFiles(removeImgFiles)                   
                
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)
            
    # 话题状态，加精，加置顶
    def patch(self,tid) :
        try:
            super().post(self)
            #user=self.getTokenToUser()
            objUser=self.objUserInfo
            user=objUser['user']            
            
            objData=self.getRequestData()
            
            # 修改状态;
            updateData={}
            
            try :
                status =objData['status']
                updateData['status']=status
            except :
                pass
            
            try :
                top = objData['top']
                updateData['isTop']=top
                if top not in ['Y','N'] : raise BaseError(801) # 参数错误
            except :
                pass 
            
            try :
                essence = objData['essence']
                updateData['isEssence']=essence
                if essence not in ['Y','N'] : raise BaseError(801) # 参数错误
            except :
                pass 
            
            if updateData=={} :
                raise BaseError(801) # 参数错误
          
            
            db=self.openDB()
            # 以下有权限问题
            rowcount=db.update('tbGroupTopics',updateData,{'id':tid}) 
            db.close()
            
            if rowcount<0 : raise BaseError(802) # SQL执行没有成功,可能是user与tid不匹配，即用户只能删除自己的话题
                
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)

    # 用户删除话题
    def delete(self,tid):
        try:
            super().post(self)
            #user=self.getTokenToUser()
            objUser=self.objUserInfo
            user=objUser['user']            

            db=self.openDB()
            db.begin()
            
            #1.1 修改话题状态;
            updateData={
                'updateTime' : '{{now()}}',
                'status'     : 'UD',
                'isDelete'   : 'Y'
            }
            rowcount=db.update('tbGroupTopics',updateData,{'id':tid,'user':user})
            db.close()
            
            if rowcount<0 :raise BaseError(802) # SQL执行没有成功,可能是user与tid不匹配，即用户只能删除自己的话题
                
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)
            
