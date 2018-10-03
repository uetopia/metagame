var controller = angular.module('angular-google-api-example.controller.admin.season.detail', []);

controller.controller('angular-google-api-example.controller.admin.season.detail', ['$scope', '$state', 'endpoints','$stateParams',
    function regionCreateCtl($scope, $state, endpoints, $stateParams) {

      $scope.seasonKeyId = $stateParams.seasonKeyId;
      $scope.season = {};

      // Load season
        endpoints.post('seasons', 'get', {'key_id': $stateParams.seasonKeyId})
            .then(function(response) {
                // DONE!
                console.log(response);
                $scope.season = response;

            }, function() {
              // ERROR!
              console.log('error');
            });


        $scope.submitUpdate = function(form) {
              if (!form.$invalid) {
                $scope.season.key_id = $stateParams.seasonKeyId;
                endpoints.post('seasons', 'update', $scope.season
                                                            ).then(function(resp) {
                    console.log(resp.response_message);
                      console.log(resp);
                      $state.go('adminHome');
                  });
              }
            };


    }
]);
