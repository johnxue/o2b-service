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
                'select' : 'id,gid,user,nickname,header,topic,summary,createTime,viewCount,replyCount,isTop,isEssence,status_code,status',
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
            
    # 新增圈子话题    
    def post(self,gid):
        try:
            super().post(self)
            user=self.getTokenToUser()
            objData=self.getRequestData()
            try:
                cat=objData['type']
                #gid=objData['gid']
                #tid=objData['tid']
                #cid=objData['cid']
                #rid=objData['rid']
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
            
            
            # 将临时图像文件移动到正式文件夹中
            try :
                lstFiles=['']*0
                if (imgFiles is not None) and (len(imgFiles)>0) :
                    lstImg=imgFiles.split(',')
                    for imgFile in lstImg :
                        imgFile_Old=imgFile.replace("/images/tmp/",config.imageConfig['temp']['path']+'/')
                        imgFileName=imgFile.split('/').pop()
                        imgFile_New=config.imageConfig[cat]['path']+'/'+imgFileName
                        os.rename(imgFile_Old,imgFile_New) # os.rename只能同盘移动，否则就是拷贝速度
                        lstFiles.append(imgFile_New)       #成功移动的文件传入lstFiles
                        # 将content中的临时URL替换成最终的URL
                        imgURL=config.imageConfig[cat]['url']+'/'+imgFileName
                        content=content.replace(imgFile,imgURL)
            except :
                # 移动失败后会将成功移动的文件删除
                self.delFiles(lstFiles)
                raise BaseError(817) # 文件移动失败  
            
            db=self.openDB()
            db.begin()
            
            #1.1 插入话题
            insertData={
                'gid'        : gid,
                'user'       : user,
                'nickname'   : 'nickname',
                'header'     : 'header',
                'topic'      : topic,
                'summary'    : summary,
                'contents'   : content,
                'viewCount'  : 0,
                'replyCount' : 0,
                'createTime' : '{{now()}}',
                'isDelete'   : 'N',
                'isTop'      : 'N',
                'isEssence'  : 'N',
                'status'     : status
            }
            topicId=db.insert('tbGroupTopics',insertData)
            db.close()
            if topicId<0 : 
                # 插入失败后删除成功移动的文件
                self.delFiles(lstFiles)
                raise BaseError(703) # SQL执行错误            

            rows={
                'gid' : gid,
                'tid' : topicId
            }
            
            self.response(rows)
                
        except BaseError as e:
            self.delFiles(lstFiles)
            self.gotoErrorPage(e.code) 
            

    # 删除一组文件
    def delFiles(self,lstFiles) :
        for f in lstFiles :
            try:
                os.remove(f)
            except :
                pass
