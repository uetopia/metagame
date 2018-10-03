var controller = angular.module('angular-google-api-example.controller.admin.region.detail', []);

controller.controller('angular-google-api-example.controller.admin.region.detail', ['$scope', '$state', 'endpoints','$stateParams',
    function regionCreateCtl($scope, $state, endpoints, $stateParams) {

      $scope.regionKeyId = $stateParams.regionKeyId;
      $scope.maps = [];

      // Load maps
        endpoints.post('maps', 'mapCollectionGet', {'regionKeyId': $stateParams.regionKeyId})
            .then(function(response) {
                // DONE!
                console.log(response);
                $scope.maps = response.maps;

            }, function() {
              // ERROR!
              console.log('error');
            });


    }
]);
