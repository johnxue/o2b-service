import tempfile,os,time,logging,random
import config
from PIL import Image
from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

# Image包安装： 
# sudo apt-get install libtiff4-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.5-dev tk8.5-dev python-tk  
# pip3 install Pillow


class uploadfile(object):
    
    # 删除一组文件，errPass为真时不对错误进行处理，为假时，不能删除文件时返回False
    def delFiles(self,lstFiles,errPass=True) :
        #lstImg=lstFiles.split(',')
        lstImg=lstFiles
        for f in lstImg :
            try:
                if config.imageRootPath not in f :  f=config.imageRootPath+f
                os.remove(f)
            except :
                if not errPass : return False
        return True
    
    # 将提交的html文件中的上传图片转移到正式图片的文件夹中，并替换html相应的图片文件名
    # imgFiles   - 存放临时文件名的字符串，文件名间用","号分隔
    # content    - 需要处理的HTML内容，如不存在可设置为''或None
    # cat        - 图片类型，系统根据图片类型自动匹配存放的目录
    # replaceStr - 该变量为元组类型，用于临时文件名中需要替换成的字符描述，如需要将临时文件中的'000000'替换成'123456'
    def preImagesAndHtml(self,imgFiles,content,cat,replaceStr=None):
        # 预处理，将临时图像文件移动到正式文件夹中
        try :
            lstFiles=['']*0
            # 判断content的内容是否为空
            if content is None or content=='' : 
                contentIsNone=True
                content=''
            else : contentIsNone=False
            if (imgFiles is not None) and (len(imgFiles)>0) :
                lstImg=imgFiles.split(',')
                for imgFile in lstImg :
                    imgFile_Old=imgFile.replace("/images/tmp/",config.imageConfig['temp']['path']+'/')
                    imgFileName_Old=imgFile.split('/').pop()
                    imgFileName_New=imgFileName_Old
                    
                    # 如果replaceStr是非空的，将进行替换
                    if replaceStr is not None :
                        imgFileName_New=imgFileName_New.replace(replaceStr[0],replaceStr[1])  
                                           
                    imgFile_New=config.imageConfig[cat]['path']+'/'+imgFileName_New
                    
                        
                    #try:
                    #    os.remove(imgFile_New)
                    #except :
                    #    pass

                    os.rename(imgFile_Old,imgFile_New) # os.rename只能同盘移动，否则就是拷贝速度
                    lstFiles.append(imgFile_New)       #成功移动的文件传入lstFiles
                    # 将content中的临时URL替换成最终的URL
                    imgURL=config.imageConfig[cat]['url']+'/'+imgFileName_New
                    if not contentIsNone :
                        content=content.replace(imgFile,imgURL)
                        content=content.replace(imgFileName_Old,imgFileName_New)
            result={
                'files'   : lstFiles,
                'content' : content
            }            
            return result
        except :
            # 移动失败后会将成功移动的文件删除
            self.delFiles(lstFiles)
            raise BaseError(817) # 文件移动失败  
                
    def uploadImages(self,uploadData):
        attribution  = uploadData['type'].lower()                 # 图像归属频道 HEADER|GROUPHEADER|PRODCUT.X|GROUP|
        maxImageSize = config.imageConfig[attribution]['size']    # 图片最大尺寸
        try :
            code = uploadData['code']          # 用户名/产品编码/圈贴ID
        except:
            code =''
        
        try:
            orderid = uploadData['orderid']       # 订单id
        except:
            orderid=''
        
        try:
            groupid = uploadData['groupid']       # 圈子id
        except:
            groupid=''
            
        try:
            user = uploadData['user']             # 用户名
        except:
            user=''        
            
  
        # 判断图片格式是否合法，图片格式有：image/jpeg，image/bmp，image/pjpeg，image/gif，image/x-png，image/png
        send_file = uploadData['files'][0]
        if send_file['content_type'] not in config.imageConfig['imageFileType'] :
            raise BaseError(811) # 无法识别的图像格式
        
        # 简单判断上传文件名后缀是否合法
        upfile_Size=len(send_file['body'])
        if upfile_Size > config.imageConfig[attribution]['size'] :
            raise BaseError(814) # 图片大小超过指定大小，最大不超过4M
        
        # 存储也就是将send_file['body']内容进行存储，type(send_file['body'])为str
        # 先将文件写入临时文件，然后再用PIL对这个临时文件进行处理。
        tmp_file = tempfile.NamedTemporaryFile(delete=True) #创建临时文件，当文件关闭时自动删除
        tmp_file.write(send_file['body'])  #写入临时文件
        tmp_file.seek(0)   #将文件指针指向文件头部，因为上面的操作将指针指向了尾部。
        #此时用PIL再处理进行存储，PIL打开不是图片的文件会出现IOERROR错误，这就可以识别后缀名虽然是图片格式，但内容并非是图片。

        try:
            im = Image.open( tmp_file.name )
        except IOError as error:
            logging.info(error)   # 进行日志记录，以防止黑客
            logging.info('+'*30 + '\n')
            #logging.info(self.request.headers)
            logging.info('非法图片格式，提交用户： '+user)
            tmp_file.close()
            raise BaseError(813) # 非法图片格式
        
        # 判断图片尺寸，不在尺寸内拒绝操作
        #if im.size[0] < 250 or im.size[1] < 250 or im.size[0] > 2000 or im.size[1] > 2000:
        #    tmp_file.close()
        #    raise BaseError(813) # 图片长宽超界
    
        # 获取文件格式，用PIL获得的format不一定正确，所以用原文件名获得
        image_path = config.imageConfig[attribution]['path']                  # 路经从config中获得
        temp_url   = config.imageConfig['temp']['url']                        # 临时URL
        image_format = '.'+send_file['filename'].split('.').pop().lower()     # 文件格式后缀转小写
        file_random=str(int(time.time())) + str(random.randint(1, 100000))    # 随机数=时间+随机数
        file_suffix=file_random+image_format   # 拼文件后缀

        '''
            指定存储目录进行存储，并产生规范的文件名。
            header      : header+'-'+user+'.jpg'
            groupheader : groupheader+'-'+group_id+'.jpg'
            prodcut     : prodcut+'-'+code+'-'+随机数+'banner|large|medium|small'+'.jpg'
            group       : group+'-'+user+'-'+group_id+'.jpg'            
        '''
        
        temp_path  = config.imageConfig['temp']['path']+'/'+time.strftime("%Y%m%d",time.localtime())  # 临时目录
        temp_url   = config.imageConfig['temp']['url']                                                # 临时目录的URL
        
        if attribution=='userheader':
            temp_path  = config.imageConfig['userheader']['path']                # 临时目录 = 真实目录
            temp_url   = config.imageConfig['userheader']['url']                 # 临时URL = 真实URL
            tmp_name='header-'+user+'-'+file_suffix                              # 注：如果用户多次更换头像可能产生一堆垃圾需要处理
        elif attribution=='groupheader':
            temp_path  = config.imageConfig['groupheader']['path']          # 临时目录 = 真实目录
            temp_url   = config.imageConfig['groupheader']['url']           # 临时URL = 真实URL
            tmp_name='groupheader-'+groupid+'-'+file_suffix                      # 注：如果用户多次更换头像可能产生一堆垃圾需要处理
        elif attribution=='news':
            tmp_name='news-'+user+'-'+file_suffix
        elif attribution=='group':
            tmp_name='group-'+user+'-'+groupid+'-'+file_suffix
        elif attribution=='order.returns' :
            tmp_name='tmp_returns-'+user+'-'+file_suffix
        elif attribution=='product.detail' :
            tmp_name='product-detail-'+code+'-'+file_suffix
        else :
            tmp_name='product-'+code+'-'+file_random+'-'+attribution.split('.').pop().lower()+image_format        
            
        try:
            
            # 如果临时目录不存在，则直接创建
            if not os.path.exists(temp_path) : os.makedirs(temp_path)
                
            im.save(temp_path+'/'+tmp_name)
            #关闭临时文件，关闭后临时文件自动删除
            tmp_file.close()
            
            # 如果是传的中等图片会自动生成一张80×80的小图
            if attribution=='product.medium' :
                new_img = im.resize((80, 80), Image.BILINEAR)
                small_name=tmp_name.replace('-medium.','-small.')
                new_img.save(temp_path+'/'+small_name)              
            
            # 替换临时URL中的时间表示 
            if '{yyyy}{mm}{dd}' in temp_url :
                temp_url=temp_url.replace("{yyyy}{mm}{dd}",time.strftime("%Y%m%d",time.localtime()))

            info={
                "url"      : temp_url,
                "filename" : tmp_name,
                "size"     : upfile_Size,
                "type"     : image_format
            }
            return info
        
        except IOError as error:
            logging.info(error)    # 进行日志记录，以防止黑客
            logging.info(temp_path+'/'+tmp_name+'文件存贮失败！ [user=%s]' % (user))
            tmp_file.close()
            raise BaseError(816)   # 非法图片格式        
    

class Handler(WebRequestHandler):
    def post(self):
        super().post(self)
        objUser=self.objUserInfo
        user=objUser['user']          
        objData=self.getRequestArguments()
            
        try :
            objData['user']=user
            
            #if objData['action']=='uploadimage' :
            objData['files']=self.request.files['upfile']
            img=uploadfile()
            rspData=img.uploadImages(objData)
            
            rspData={
                "state": "SUCCESS",
                "url": rspData['url']+'/'+rspData['filename'],
                "filename": rspData['filename'],
            }
            
            if objData['type']=='header':
                updateData={
                    'img_header'  : rspData["filename"],
                    'updateTime'   : self._now_time_,
                    'updateUser'   : user
                }            
                        
                db=self.openDB()
                ur=db.updateByPk('tbUser',updateData,user,pk='user')
                if ur<=0 :BaseError(802) # 没有数据找到
                self.closeDB()            
            
            self.response(rspData,angluar=False) # 返回查询结果        

        except BaseError as e:
            self.gotoErrorPage(e.code)
