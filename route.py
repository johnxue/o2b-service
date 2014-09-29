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

import Order.list
import Order.detail
import Order.attribute
import Order.Returns.list


import User.follow
import User.changePassword

import Service.uploadfile

import Group.attribute,Group.manage

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
            (r"/o2b/v1.0.0/group", Group.manage.info),            
            
            #广告
            (r"/o2b/v1.0.0/adSense/(.*)/([0-9]+)", AdSense.list.info),
            #服务
            (r"/o2b/v1.0.0/service/uploadfile", Service.uploadfile.Handler),
            
            #其它
            (r"/o2b/v1.0.0/apis", ApiLib.list.Handler),
            (r".*", Framework.Base.Base404Handler),
            

        ]