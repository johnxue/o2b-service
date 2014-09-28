import tempfile
from PIL import Image
import time
import logging
import config

from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

class Handler(WebRequestHandler):
    def post(self):
        try :
            super().post(self)
            user=self.getTokenToUser()
            objData=self.getRequestArguments()
            if objData=={} :
                raise BaseError(801) # 参数错误
                
            attribution=objData['type'].lower()  # 图像归属频道 HEADER|PRODCUT|GROUP
            try :
                code       =objData['code']      # 用户名/产品编码/圈贴ID
            except:
                code =''
            try :
                orderid    =objData['orderid']   # 订单id
            except :
                orderid=''
            try :
                groupid    =objData['groupid']   # 圈子id
            except :
                groupid=''            
            
            # 看是HTML传过来的JSON Key 是否为 picture
            if self.request.files == {} or 'picture' not in self.request.files \
               or attribution not in "header,product.banner,product.large,product.medium,product.small,order.returns,group" :
                raise BaseError(801) # 参数错误
            
            # 判断图片格式是否合法，图片格式有：image/jpeg，image/bmp，image/pjpeg，image/gif，image/x-png，image/png
            image_type_list = ['image/gif', 'image/jpeg', 'image/pjpeg', 'image/bmp', 'image/png', 'image/x-png']
            send_file = self.request.files['picture'][0]
            if send_file['content_type'] not in image_type_list:
                raise BaseError(811) # 无法识别的图像格式
            
            
            # 简单判断上传文件名后缀是否合法
            if len(send_file['body']) > 4 * 1024 * 1024:
                raise BaseError(814) # 图片大小超过4M
            
            # 满足要求后，将图片存储。
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
                logging.info(self.request.headers)
                logging.info('提交用户： '+user)
                tmp_file.close()
                raise BaseError(813) # 非法图片格式
            
            # 判断图片尺寸，不在尺寸内拒绝操作
            #if im.size[0] < 250 or im.size[1] < 250 or im.size[0] > 2000 or im.size[1] > 2000:
            #    tmp_file.close()
            #    raise BaseError(813) # 图片长宽超界
        
            # 获取文件格式，用PIL获得的format不一定正确，所以用原文件名获得
            image_path = config.imageConfig[attribution]['path']                  # 路经从config中获得
            temp_path  = config.imageConfig['temp']['path']                       # 临时目录
            image_format = '.'+send_file['filename'].split('.').pop().lower()     # 后缀转小写

            '''
                指定存储目录进行存储，并产生规范的文件名。
                header  : header+'-'+user+'.jpg'
                prodcut : prodcut+'-'+code+'-'+'banner|large|medium|small'+'.jpg'
                group   : group+'-'+user+'-'+gourp_id+'.jpg'            
            '''
            
            if attribution=='header':
                tmp_name='header-'+user+image_format
            elif attribution=='group':
                tmp_name='group-'+user+'-'+groupid+image_format
            elif attribution=='order.returns' :
                tmp_name='returns-'+orderid+'-'+user+'-'+code+image_format
            else :
                tmp_name='prodcut-'+code+'-'+attribution.split('.').pop().lower()+image_format
                
           
            #tmp_name = image_path +'/'+str(int(time.time())) + '.'+image_format
            #im.save(image_path+'/tmp_'+tmp_name)
            im.save(temp_path+'/'+tmp_name)
            
            file={
                'paht'     : temp_path,          #返回的是临时文件夹 image_path,
                'filename' : tmp_name
            }
        
            #关闭临时文件，关闭后临时文件自动删除
            tmp_file.close()
            self.response(file)  # 返回查询结果
        except BaseError as e:
            self.gotoErrorPage(e.code)
