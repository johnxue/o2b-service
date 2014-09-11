var loginDirective = angular.module('loginDirective', []);

//var EMAIL_REGEXP = /^[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$/;
//var MOBILE_REGEXP= /^0?(13|15|18|17)[0-9]{9}$/;

var EMAIL_AND_MOBILE_REGEXP=/[^\._-][\w\.-]+@(?:[A-Za-z0-9]+\.)+[A-Za-z]+$|^0\d{2,3}\d{7,8}$|^1[358]\d{9}$|^147\d{8}/;

loginDirective.directive('emailmobile', function() {
  return {
    require: 'ngModel',
    link: function(scope, elm, attrs, ctrl) {
      ctrl.$parsers.unshift(function(viewValue) {
        // 匹配email&mobile
        if (EMAIL_AND_MOBILE_REGEXP.test(viewValue)) {
          // it is valid
          ctrl.$setValidity('emailmobile', true);
          return viewValue;
        } else {
          // it is invalid, return undefined (no model update)
          ctrl.$setValidity('emailmobile', false);
          return undefined;
        }
      });
    }
  };
});