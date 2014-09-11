// 生成16位随机key
randomKey=function(length) {
    //var chars = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ0123456789`=//[];',./~!@#$%^&*()_+|{}:<>?";
    var chars = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ0123456789";

    var s = "";

    for(i=0; i<length; i++) {
        s += chars.charAt(Math.ceil(Math.random()*1000)%chars.length);
    }
    return s;
}


//取得Request参数
Request= {
    get:function(paras){
        var url = location.href;
        var paraString = url.substring(url.indexOf("?") + 1, url.length).split("&");
        var paraObj = {};
        var i,j;
        for ( i = 0;  j = paraString[i]; i++) {
            paraObj[j.substring(0, j.indexOf("=")).toLowerCase()] = j.substring(j.indexOf("=") + 1, j.length);
        }
        var returnValue = paraObj[paras.toLowerCase()];
        if (typeof (returnValue) == "undefined") {
            return "";
        } else {
            return returnValue;
        }
    }
};

//字符串补零
ZeroPadding={
    left:function(str,length) {
        if(str.length >= length)
            return str;
        else
            return ZeroPadding.left("0" +str,length);
    },
    right:function(str,length) {
        if(str.length >= length)
            return str;
        else
            return ZeroPadding.right(str+"0",length);
    }
}


//获得URL相关
URL={
    getAll:function() {
        return window.location.href;
    },
    getProtocol: function() {
        return window.location.protocol;

    },
    getHost:function() {
        return window.location.host;
    },
    getPort:function() {
        return window.location.port;
    },
    getPathName:function() {
        return window.location.pathname;
    },
    getSearch:function() {
        return window.location.search
    },
    getHash:function(){
        return window.location.hash;
    }

}



//本地数据存储
var localDataStorage = {
    setItem:function(key,value){
        localStorage.setItem(key,value);
    },
    getItem:function(key){
        return localStorage.getItem(key);
    },
    removeItem:function(key){
        return localStorage.removeItem(key);
    },
    clearItem:function(){
        localStorage.clear();
    },
};
