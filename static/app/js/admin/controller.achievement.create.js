var controller = angular.module('angular-google-api-example.controller.admin.achievement.create', []);

controller.controller('angular-google-api-example.controller.admin.achievement.create', ['$scope', '$state', 'endpoints',
    function mapCreateCtl($scope, $state, endpoints) {

      $scope.achievement = {};


      $scope.submitAdd = function() {
        //$state.go('home');
        endpoints.post('achievements', 'create', $scope.achievement)
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
