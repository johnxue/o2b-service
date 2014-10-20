import tempfile
import re,json,os,datetime

# Image包安装： 
# sudo apt-get install libtiff4-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.5-dev tk8.5-dev python-tk  
# pip3 install Pillow

from PIL import Image
import time
import logging
import config

from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode

from Service.uploadfile import uploadfile

class Handler(WebRequestHandler):
    def __init(self):
        self._db_=None
        self._now_time_ = datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')
    
    def get(self):
        try :
            self.__init()
            #super().post(self)
            #user=self.getTokenToUser()
            #objRequestBody=self.getRequestData()
            objData=self.getRequestArguments()
            rspData={}
            if objData['action']=='config' :
                try:
                    f = open(os.path.dirname(__file__)+'/config.json')
                    josnText=f.read()
                    f.close
                except :
                    raise BaseError(890) # 读 config.json 配置文件失败
                    
                reobj = re.compile("\/\*[\s\S]+?\*\/")
                josnText = reobj.sub('', josnText)
                rspData=json.loads(josnText)
            try:
                CallBack=objData['callback']
            except:
                CallBack=None
            self.response(rspData,angluar=False,callback=CallBack)        # 返回查询结果
        except BaseError as e:
            self.gotoErrorPage(e.code)
            
    def post(self) :
        try :
            #super().post(self)
            self.__init()
            objData=self.getRequestArguments()
            try :
                if objData['app-key']!=config.App_Key: raise BaseError(601)
                user=self._tokenToUser(objData['Authorization'])
            except:
                raise BaseError(601)
            
            objData['user']=user
            
            if objData['action']=='uploadimage' :
                objData['files']=self.request.files['upfile']
                img=uploadfile()
                rspData=img.uploadImages(objData)
                
                rspData={
                    "state": "SUCCESS",
                    "url": rspData['url']+'/'+rspData['filename'],
                    "title": rspData['filename'],
                    "original": rspData['filename'],
                    "type":rspData['type'],
                    "size":rspData['size']
                }                
                self.response(rspData,angluar=False) # 返回查询结果
        except BaseError as e:
            self.gotoErrorPage(e.code)
            
