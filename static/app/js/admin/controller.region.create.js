var controller = angular.module('angular-google-api-example.controller.admin.region.create', []);

controller.controller('angular-google-api-example.controller.admin.region.create', ['$scope', '$state', 'endpoints',
    function regionCreateCtl($scope, $state, endpoints) {

      $scope.region = {};

      $scope.submitAdd = function() {
        //$state.go('home');
        endpoints.post('regions', 'create', $scope.region)
            .then(function(response) {
                // DONE!
                console.log(response);
                $state.go('home');

            }, function() {
              // ERROR!
              console.log('error');
            });
      }


    }
]);
