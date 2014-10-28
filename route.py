import Framework.Base

import easyOAuth.login
import easyOAuth.logout
import easyOAuth.heartbeat

import Product.attribute
import Product.list
import Product.detail
import Product.follow

import Address.list
import Address.userAddress

import AdSense.list

import News.list
import News.detail

import ShoppingCart.list

from Order import attribute,list,detail
#import Order.list
#import Order.detail
#import Order.attribute

import Order.Returns.list



import User,Group,Service,Message

#.uploadfile,Service.RichEditor
#import Group.attribute,Group.list,Group.usermanage,Group.userAction,Group.userinfo,Group.groupinfo

from User         import list,detail,follow,changePassword
from User         import list,detail,follow,changePassword

from Message      import list,detail,sniffing,send

from Group        import attribute,list,usermanage,userAction,userinfo,groupinfo,Topics
from Group.Topics import list,detail,commentDetail,commentReply

#import Group.Topics.list
#import Group.Topics.detail
#import Group.Topics.commentDetail
#import Group.Topics.commentReply


from Service import uploadfile,RichEditor

import ApiLib.list



handlers = [
            # 新闻
            (r"/o2b/v1.0.0/news", News.list.info),
            (r"/o2b/v1.0.0/news/([0-9]+)", News.detail.info),
            
            #地址
            (r"/o2b/v1.0.0/area", Address.list.info),
            (r"/o2b/v1.0.0/address", Address.userAddress.list),
            (r"/o2b/v1.0.0/address/([0-9]+)", Address.userAddress.list),

            #登入/登出
            (r"/o2b/v1.0.0/login/(.*)/(.*)", easyOAuth.login.Handler),
            (r"/o2b/v1.0.0/logout", easyOAuth.logout.Handler),
            (r"/o2b/v1.0.0/service/heartbeat", easyOAuth.heartbeat.Handler),

            # 用户管理
            (r"/o2b/v1.0.0/user/product/follow", User.follow.info),
            (r"/o2b/v1.0.0/user/info/pmssmed", User.changePassword.Handler),
            (r"/o2b/v1.0.0/user/header", Service.uploadfile.Handler),
            (r"/o2b/v1.0.0/user/(.*)/info", User.detail.Handler),
            (r"/o2b/v1.0.0/user", User.list.Handler),
            
            #(r"/o2b/v1.0.0/user/info", User.follow.info)
            
            #产品管理
            (r"/o2b/v1.0.0/product/([0-9]+)/follow", Product.follow.hFollow),
            (r"/o2b/v1.0.0/product/([0-9]+)", Product.detail.info),
            (r"/o2b/v1.0.0/product/attribute", Product.attribute.info),
            (r"/o2b/v1.0.0/product", Product.list.info),
            (r"/o2b/v1.0.0/product/([0-9]+)/images", Service.uploadfile.Handler),
            
    
            #购物车管理
            (r"/o2b/v1.0.0/shoppingcart", ShoppingCart.list.info),
    
            #订单管理
            (r"/o2b/v1.0.0/order", Order.list.info),
            (r"/o2b/v1.0.0/order/([0-9]+)", Order.detail.info),
            (r"/o2b/v1.0.0/order/attribute", Order.attribute.info),
            (r"/o2b/v1.0.0/order/returns", Order.Returns.list.info),
            (r"/o2b/v1.0.0/order/returns/upload", Service.uploadfile.Handler),
            
            #圈子
            (r"/o2b/v1.0.0/group/attribute", Group.attribute.info),
            (r"/o2b/v1.0.0/group", Group.list.info),
            (r"/o2b/v1.0.0/group/([0-9]+)", Group.usermanage.Handler),
            (r"/o2b/v1.0.0/group/([0-9]+)/user", Group.userAction.Handler),
            (r"/o2b/v1.0.0/group/([0-9]+)/info", Group.groupinfo.Handler),
            (r"/o2b/v1.0.0/user/group", Group.userinfo.Handler),
            
            
            #(r"/o2b/v1.0.0/group/([0-9]+)", Group.manage.Handler),
            #(r"/o2b/v1.0.0/group/([0-9]+)/topic", Group.topic.Handler),
            #(r"/o2b/v1.0.0/group/topic/([0-9]+)", Group.topic.Handler),
            (r"/o2b/v1.0.0/group/header", Group.list.info),
            
            # 话题
            (r"/o2b/v1.0.0/group/([0-9]+)/topics", Group.Topics.list.Handler),
            (r"/o2b/v1.0.0/group/topics/([0-9]+)", Group.Topics.detail.Handler),
            (r"/o2b/v1.0.0/group/topics/([0-9]+)/comment", Group.Topics.commentDetail.Handler),
            (r"/o2b/v1.0.0/group/topics/comment/([0-9]+)/reply", Group.Topics.commentReply.Handler),

            # 消息
            (r"/o2b/v1.0.0/message/sendto/(.*)", Message.send.Handler),
            (r"/o2b/v1.0.0/message/sniffing", Message.sniffing.Handler),
            (r"/o2b/v1.0.0/message/(unread|read)", Message.list.Handler),
            (r"/o2b/v1.0.0/message/(.*)", Message.detail.Handler),
            
            
            #广告
            (r"/o2b/v1.0.0/adSense/(.*)/([0-9]+)", AdSense.list.info),
            #服务
            (r"/o2b/v1.0.0/service/uploadfile", Service.uploadfile.Handler),
            (r"/o2b/v1.0.0/service/EditHtml", Service.RichEditor.Handler),
            
            
            #其它
            (r"/o2b/v1.0.0/apis", ApiLib.list.Handler),
            (r".*", Framework.Base.Base404Handler),
            

        ]