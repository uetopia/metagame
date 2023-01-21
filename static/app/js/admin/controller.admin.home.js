var controller = angular.module('angular-google-api-example.controller.admin.home', []);

controller.controller('angular-google-api-example.controller.admin.home', ['$scope', '$rootScope', '$state', '$stateParams', '$filter', 'fbModels', 'endpoints',
    function homeCtl($scope, $rootScope, $state, $stateParams, $filter, fbModels, endpoints) {
      console.log('adminHomeCtl');

      $scope.regions = [];
      $scope.seasons = [];
      $scope.regionsLoaded = false;

      // Load Regions
      endpoints.post('regions', 'regionCollectionGet')
          .then(function(response) {
              // DONE!
              console.log(response);
              $scope.regions = response.regions
          }, function() {
            // ERROR!
            console.log('error');
          });

      // Load Seasons
      endpoints.post('seasons', 'collectionGet')
          .then(function(response) {
              // DONE!
              console.log(response);
              $scope.seasons = response.seasons
          }, function() {
            // ERROR!
            console.log('error');
          });

      // Load Achievements
      endpoints.post('achievements', 'collectionGet')
          .then(function(response) {
              // DONE!
              console.log(response);
              $scope.achievements = response.achievements
          }, function() {
            // ERROR!
            console.log('error');
          });



    }
]);
