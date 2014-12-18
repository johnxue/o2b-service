from Framework.Base  import WebRequestHandler,BaseError
from mysql.connector import errors,errorcode
import config

import smtplib
#import mimetypes
#import email
from email.mime.multipart   import MIMEMultipart
from email.mime.text        import MIMEText
from email.mime.image       import MIMEImage
from email.mime.application import MIMEApplication  

#from email.mime.base       import MIMEBase
#from email import Encoders


class Handler(WebRequestHandler):

    def post(self):
        try :
            super().get(self)
            objUser=self.objUserInfo
            user=objUser['user']             
            objData=self.getRequestData()
            data={}
            
            # 发件人
            try:
                data['fromAdd']=objData['from']
            except:
                data['fromAdd']=config.EmailConfig['fromAdd']
            
            lstData={
                'toAdd'       : 'to',    # 收件人
                'subject'     : 'sub',   # 邮件主题
                'type'        : 'type',  # 邮件类型 
                'body'        : 'body',  # 内容
                'images'      : 'img',   # 逗号分隔的图片
                'attachments' : 'att'    # 逗号分隔的附件
            }
            
            for (k,v) in lstData.items():
                try:
                    if objData[v] is not None :
                        data[k]=objData[v]
                except:
                    data[k]=''
                    
            # 对不同邮件类型的处理，注册检验邮件
            if data['type'].lower()=='verification' :
                data['body'] = config.EmailConfig['content_verification']
                data['subject'] = config.EmailConfig['subject_verification']
                
            # 无邮件内容及主题或无收件人时抛错     
            if (data['body']+data['subject'])=='' or data['toAdd']=='' :
                raise BaseError(801) # 参数错误  
                
            self.sendEmail(data)
            self.response()
        except BaseError as e:
            self.gotoErrorPage(e.code)
    
    
    def addAttachment(self,strFile,type='attachment',index=0):
        att=None
        filename=strFile.split('/').pop()
        if type=='attachment' :
            att = MIMEApplication(open(strFile,'rb').read())
            att.add_header('Content-Disposition', 'attachment', filename="%s" % (filename,))
        elif type=='image' :
            att = MIMEImage(open(strFile,'rb').read())
            att.add_header('Content-ID', '<image%s>' % (index,))
        return att
    
    def sendEmail(self,email):
        #def sendEmail(fromAdd,toAdd, subject, plainText, htmlText):
        strFrom = email['fromAdd']
        strTo   = email['toAdd']
        server  = config.EmailConfig['server']['smtp.server']
        user    = config.EmailConfig['server']['username']
        passwd  = config.EmailConfig['server']['password']
        if not (server and user and passwd) :
            return 0
        # 设定root信息
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = email['subject']
        msgRoot['From'] = strFrom
        msgRoot['To'] = strTo
        msgRoot.preamble = 'This is a multi-part message in MIME format.' 
        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative) 

        #设定纯文本信息
        plainText = email['body']
        htmlText = email['body']
        #msgText = MIMEText(plainText, 'plain', 'utf-8')
        #msgAlternative.attach(msgText) 

        #设定HTML信息
        msgText = MIMEText(htmlText, 'html', 'utf-8')
        msgAlternative.attach(msgText)
        
        
        #设定内置图片信息
        #fp = open('test.jpg', 'rb')
        #msgImage = MIMEImage(fp.read())
        #fp.close()
        #msgImage.add_header('Content-ID', '<image1>')
        #msgRoot.attach(msgImage) 
        #发送邮件
        
        #处理图片
        if email['images'] :
            listFiles=email['images'].split(',')
            i=1
            for file in listFiles:
                att = self.addAttachment(file,'image',i)
                msgRoot.attach(att)
                i+=1
        
        #处理附件
        if email['attachments'] :
            listFiles=email['attachments'].split(',')
            for file in listFiles:
                att = self.addAttachment(file)
                msgRoot.attach(att)
        
        smtp = smtplib.SMTP()
        #设定调试级别，依情况而定
        smtp.set_debuglevel(1)
        smtp.connect(server)
        smtp.login(user, passwd)
        smtp.sendmail(strFrom, strTo, msgRoot.as_string())
        smtp.quit()
        return 

