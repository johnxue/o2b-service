'use strict';

/* Services */

var loginServices = angular.module('loginServices', ['ngResource']);

loginServices.factory('loginServices', function($http){
    var baseUrl="/o2b/v1.0.0/login";
    return {
        getToken: function (uri, funSuccess, funError) {
            $http.get(baseUrl + uri).success(funSuccess).error(funError);
        }
    }
});

