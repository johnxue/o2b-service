from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

class info(WebRequestHandler):
    def get(self):
        try :
            super().get(self)
            
            offset   = int(self.get_argument("o",default='0'))
            rowcount = int(self.get_argument("r",default='1000'))
        
            db = self.openDB()
            
            #1.1 查询产品属性；
            conditions={
                'select' : 'id,title,author,source,summary,createTime,topLevel,CTR,status_code,status',
                'where'  : 'status_code="OK"',
                'limit'  : '%s,%s' % (offset,rowcount)
            }
            rows_list = db.getAllToList('vwNews',conditions)

            self.closeDB()
            
            if len(rows_list)==0:
                raise BaseError(802) # 未找到数据
            
            #3. 打包成json object
            rows = {'news' : rows_list }
            self.response(rows)
            
        except BaseError as e:
            self.gotoErrorPage(e.code)


    # 新增新闻  
    def post(self,gid):
        try:
            super().post(self)
            user=self.getTokenToUser()
            objData=self.getRequestData()
            try:
                cat=objData['type']
                title=objData['title']
                author = objData['author']
                summary = objData['summary']
                source = objData['source']
                content=objData['content']
                imgFiles=objData['imgFiles']
                status=objData['status']
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
            
            #1.1 插入新闻
            insertData={
                'createUser' : user,
                'nickname'   : 'nickname',
                'header'     : 'header',
                'title'      : title,
                'summary'    : summary,
                'author'     : author,
                'source'     : source,
                'htmlContent': content,
                'viewCount'  : 0,
                'replyCount' : 0,
                'createTime' : '{{now()}}',
                'isDelete'   : 'N',
                'topLevel'   : 0,
                'CTR'        : 0,
                'status'     : status
            }
            newsId=db.insert('tbNews',insertData)
            db.close()
            if newsId<0 : 
                # 插入失败后删除成功移动的文件
                self.delFiles(lstFiles)
                raise BaseError(703) # SQL执行错误            

            rows={
                'id' : newsId
            }
        
            self.response(rows)
            
        except BaseError as e:
            self.delFiles(lstFiles)
            self.gotoErrorPage(e.code) 