var controller = angular.module('angular-google-api-example.controller.admin.achievement.detail', []);

controller.controller('angular-google-api-example.controller.admin.achievement.detail', ['$scope', '$state', 'endpoints','$stateParams',
    function achievementDetailCtl($scope, $state, endpoints, $stateParams) {

      $scope.achievementKeyId = $stateParams.achievementKeyId;

      // get the region
      endpoints.post('achievements', 'get', {'key_id': $stateParams.achievementKeyId})
            .then(function(response) {
                // DONE!
                console.log(response);
                $scope.achievement = response;

                //$state.go('home');
            }, function() {
              // ERROR!
              console.log('error');
            });

        //  submit
        $scope.submit = function() {
          $scope.achievement.key_id = $stateParams.achievementKeyId;
            endpoints.post('achievements', 'update', $scope.achievement)
                  .then(function(response) {
                      // DONE!
                      console.log(response);
                      $state.go('home');
                  }, function() {
                    // ERROR!
                    console.log('error');
                  });

        };


    }
]);
