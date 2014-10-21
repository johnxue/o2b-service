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
    # 用户查询圈子的某一个话题具体内容
    def get(self,tid):
        try :
            super().get(self)
            
            # 分页
            offset=int(self.get_argument("o",default=0))
            rowcount=int(self.get_argument("r",default=1000))
            offset=offset*rowcount
            user=self.getTokenToUser()
                
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
    def post(self,tid):
        try:
            super().post(self)
            user=self.getTokenToUser()
            objData=self.getRequestData()
            try:
                cat=objData['type']
                topic=objData['topic']
                summary = objData['summary']
                content=objData['content']
                imgFiles=objData['imgFiles']
                try :
                    status =objData['status']
                except :
                    status =None          
            except :
                raise BaseError(801) # 参数错误
            
           
            # 将临时图像文件移动到正式文件夹中
            try :
                if (imgFiles is not None) and (len(imgFiles)>0) :
                    lstImg=imgFiles.split(',')
                    for imgFile in lstImg :
                        imgFile_Old=imgFile.replace("/images/tmp/",config.imageConfig['temp']['path']+'/')
                        imgFileName=imgFile.split('/').pop()
                        imgFile_New=config.imageConfig[cat]['path']+'/'+imgFileName
                        os.rename(imgFile_Old,imgFile_New) # os.rename只能同盘移动，否则就是拷贝速度
                        # 将content中的临时URL替换成最终的URL
                        imgURL=config.imageConfig[cat]['url']+'/'+imgFileName
                        content=content.replace(imgFile,imgURL)
            except :
                # 插入失败后删除成功移动的文件
                self.delFiles(lstFiles)                
                raise BaseError(817) # 文件移动失败     
            
            db=self.openDB()
            db.begin()
            
            #1.1 修改话题;
            updateData={
                'nickname'   : 'nickname',
                'header'     : 'header',
                'updateTime' : '{{now()}}'
            }
            
            # 如果内容为None即不修改
            if topic   is not None : updateData['topic']    = topic
            if content is not None : updateData['contents'] = content
            if status  is not None : updateData['status']   = status
            if summary is not None : updateData['summary']  = summary
                
            rowcount=db.update('tbGroupTopics',updateData,{'id':tid,'user':user}) 
            db.close()
            
            if rowcount<0 :
                # 更改失败后删除成功移动的文件
                self.delFiles(lstFiles)                
                raise BaseError(802) # SQL执行没有成功,可能是user与tid不匹配，即用户只能删除自己的话题            

            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)        
    
        

    # 用户删除话题
    def delete(self,tid):
        try:
            super().post(self)
            user=self.getTokenToUser()
            objData=self.getRequestData()
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
            
    # 删除一组文件
    def delFiles(self,lstFiles) :
        for f in lstFiles :
            try:
                os.remove(f)
            except :
                pass

         
            
        
        
