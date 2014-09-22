import easyOAuth.login
import easyOAuth.logout
import easyOAuth.heartbeat
import easyOAuth.changePassword

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
import Framework.Base

handlers = [
            (r"/o2b/v1.0.0/news", News.list.info),
            (r"/o2b/v1.0.0/news/([0-9]+)", News.detail.info),
    
            (r"/o2b/v1.0.0/area", Address.list.info),
            (r"/o2b/v1.0.0/address", Address.userAddress.list),
            (r"/o2b/v1.0.0/address/([0-9]+)", Address.userAddress.list),

            (r"/o2b/v1.0.0/login/(.*)/(.*)", easyOAuth.login.Handler),
            (r"/o2b/v1.0.0/logout", easyOAuth.logout.Handler),
            (r"/o2b/v1.0.0/changepassword", easyOAuth.changePassword.Handler),
            
            (r"/o2b/v1.0.0/service/heartbeat", easyOAuth.heartbeat.Handler),

            (r"/o2b/v1.0.0/product/([0-9]+)/follow", Product.follow.hFollow),
            (r"/o2b/v1.0.0/product/([0-9]+)", Product.detail.info),
            (r"/o2b/v1.0.0/product/attribute", Product.attribute.info),
            (r"/o2b/v1.0.0/product", Product.list.info),
    
            (r"/o2b/v1.0.0/shoppingcart", ShoppingCart.list.info),
    
            (r"/o2b/v1.0.0/order", Order.list.info),
            (r"/o2b/v1.0.0/order/([0-9]+)", Order.detail.info),
            (r"/o2b/v1.0.0/order/attribute", Order.attribute.info),
            (r"/o2b/v1.0.0/order/returns", Order.Returns.list.info),

            (r"/o2b/v1.0.0/adSense/(.*)/([0-9]+)", AdSense.list.info),
            (r".*", Framework.Base.Base404Handler),

        ]