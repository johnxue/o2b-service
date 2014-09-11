'use strict';

/* App Module */
var loginApp = angular.module('loginApp', [
    'ngRoute',
    'loginControllers',
    'loginDirective',
    'loginServices'
]);

loginApp.config(['$routeProvider',
    function($routeProvider) {
        $routeProvider.
            when('/login', {
                title:'CRM登录',
                templateUrl: 'templates/tmpLogin.html',
                controller: 'loginCtrl'
            }).
            when('/logout', {
                title:'CRM登出',
                templateUrl: 'templates/tmpLogout.html',
                controller: 'logoutCtrl'
            }).
            otherwise({
                redirectTo: '/login'
            })
}]);


loginApp.run(['$location', '$rootScope', function($location, $rootScope) {
     $rootScope.$on('$routeChangeSuccess', function(currentRoute, previousRoute) {
        $rootScope.title = previousRoute.$$route.title;
    });
}]);


