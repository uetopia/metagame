var controller = angular.module('angular-google-api-example.controller.uetopia.connect', []);

controller.controller('angular-google-api-example.controller.uetopia.connect', ['$scope', '$state', 'endpoints',
    function addCtl($scope, $state, endpoints) {

      $scope.resultModel = {};

      $scope.submitAdd = function() {
        //$state.go('home');
        endpoints.post('users', 'uetopiaValidate', {security_code: $scope.resultModel.security_code})
            .then(function(response) {
                // DONE!
                console.log(response);
                if (response.response_message === "Firebase Unauth.") {
                  console.log('Firebase Unauth');

                  //auth.refreshtoken();
                } else {
                  $state.go('home');
                }

            }, function() {
              // ERROR!
              console.log('error');
            });
      }


    }
]);
