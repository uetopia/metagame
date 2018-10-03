var controller = angular.module('angular-google-api-example.controller.home', []);

controller.controller('angular-google-api-example.controller.home', ['$scope', '$rootScope', '$state', '$stateParams', '$filter', 'fbModels', 'endpoints','$firebaseArray',
    function homeCtl($scope, $rootScope, $state, $stateParams, $filter, fbModels, endpoints, $firebaseArray) {
      console.log('homeCtl');

      $scope.regions = [];

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

        // Load factions from firebase
        var faction_ref = firebase.database().ref().child('factions').orderByChild('-control');
        $scope.factions = $firebaseArray(faction_ref);

    }
]);
