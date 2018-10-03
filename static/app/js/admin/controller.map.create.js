var controller = angular.module('angular-google-api-example.controller.admin.map.create', []);

controller.controller('angular-google-api-example.controller.admin.map.create', ['$scope', '$state', 'endpoints',
    function mapCreateCtl($scope, $state, endpoints) {

      $scope.map = {};
      $scope.regions = [];
      $scope.seasons = [];

      $scope.submitAdd = function() {
        //$state.go('home');
        endpoints.post('maps', 'create', $scope.map)
            .then(function(response) {
                // DONE!
                console.log(response);
                $state.go('home');

            }, function() {
              // ERROR!
              console.log('error');
            });
      }

      // Get the regions to populate the dropdown
      endpoints.post('regions', 'regionCollectionGet')
          .then(function(response) {
              // DONE!
              console.log(response);
              $scope.regions = response.regions
          }, function() {
            // ERROR!
            console.log('error');
          });

      // Get the seasons to populate the dropdown
      endpoints.post('seasons', 'collectionGet')
          .then(function(response) {
              // DONE!
              console.log(response);
              $scope.seasons = response.seasons
          }, function() {
            // ERROR!
            console.log('error');
          });


    }
]);
