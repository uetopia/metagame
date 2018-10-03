var controller = angular.module('angular-google-api-example.controller.admin.season.create', []);

controller.controller('angular-google-api-example.controller.admin.season.create', ['$scope', '$state', 'endpoints',
    function regionCreateCtl($scope, $state, endpoints) {

      $scope.season = {};

      $scope.submitAdd = function() {
        //$state.go('home');
        endpoints.post('seasons', 'create', $scope.season)
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
