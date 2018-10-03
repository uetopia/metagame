var controller = angular.module('angular-google-api-example.controller.add', []);

controller.controller('angular-google-api-example.controller.add', ['$scope', '$state', 'endpoints',
    function addCtl($scope, $state, endpoints) {

      $scope.submitAdd = function() {
        $state.go('home');
        endpoints.post('seed', 'modelCreate', {name: $scope.model.name, description: $scope.model.description})
            .then(function(response) {
                // DONE!
                console.log(response);
                if (response.response_message === "Firebase Unauth.") {
                  console.log('Firebase Unauth');

                  //auth.refreshtoken();
                }

            }, function() {
              // ERROR!
              console.log('error');
            });
      }


    }
]);
