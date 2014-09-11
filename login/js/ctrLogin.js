'use strict';

//$httpProvider.defaults.headers.post['My-Header']='value'   (or)
//$http.defaults.headers.post['My-Header']='value';

//appkey=fb98ab9159f51fd0
//secret=09f7c8cba635f7616bc131b0d8e25947

/* Controllers */
var loginControllers = angular.module('loginControllers', []);

loginControllers.controller('loginCtrl', function ($scope,$window,loginServices) {
	
   // 点击提交
    $scope.update = function(objLoginInfo) {
        // 得到Key及iv
        var strMD5Passwd = CryptoJS.MD5(objLoginInfo.password).toString();
        var strRandomIV = randomKey(16);
        var strData = Request.get('url');

        var key  = CryptoJS.enc.Utf8.parse(strMD5Passwd);
        var iv  = CryptoJS.enc.Utf8.parse(strRandomIV);

        var strAesEncrypted = CryptoJS.AES.encrypt(strData, key,
            { iv: iv, mode:CryptoJS.mode.CBC,padding:CryptoJS.pad.ZeroPadding});


        var strUserName=objLoginInfo.username;
        var strUserNameLength=ZeroPadding.left(strUserName.length,3);

        var strDataPacket=strRandomIV+strUserNameLength+strAesEncrypted+strUserName;

        var id=Request.get('id');
        var secret=Request.get('secret');
        var url=Request.get('url').toLowerCase();



        console.log('DataPacket: ' + strDataPacket);
        console.log('DataPacket Base64 :'+Base64.encode(strDataPacket));
        console.log('DataPacket Base64 decode:'+Base64.decode(Base64.encode(strDataPacket)));


        strDataPacket="/id/"+id+"/secret/"+secret+"/url/"+url+"/data/"+Base64.encode(strDataPacket);

        var objResults={
            error : {code : 0,message : ''},
            authcode:''
        };


        loginServices.getToken(strDataPacket,function(response, status, headers, config){
            objResults.authcode=headers('Authorization');
            url=url+'?code='+objResults.authcode;
            alert(url);
            $scope.appid = objResults.authcode;
            $window.location.href= url;
            // 调用回调连接
        },function(response){
            objResults.error.code=parseInt(response.code);
            objResults.error.message=response.message;
            $scope.xue=!$scope.xue;
            // 处理错误
        });

    }


    $scope.reset = function() {
    	$scope.objLoginInfo = {};
        $scope.abc=!($scope.abc);
    };

    $scope.isUnchanged = function(objLoginInfo) {
    	return angular.equals(objLoginInfo, $scope.master);
    };


    /* 结束 ---方法申明  */

    /* 初始化代码块 -- 开始... */

    $scope.strSubhead =" - 登录";
    $scope.appid='*';
    $scope.master= {};
    $scope.reset();

    /* 结束 --初始化代码块  */


});

loginControllers.controller('logoutCtrl', function ($scope) {
    $scope.strSubhead =" - 登出";
});

