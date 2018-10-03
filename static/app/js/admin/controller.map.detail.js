var controller = angular.module('angular-google-api-example.controller.admin.map.detail', []);

controller.controller('angular-google-api-example.controller.admin.map.detail', ['$scope', '$state', 'endpoints','$stateParams','$firebaseArray',
    function regionCreateCtl($scope, $state, endpoints, $stateParams, $firebaseArray) {

      $scope.regionKeyId = $stateParams.regionKeyId;
      $scope.mapKeyId = $stateParams.mapKeyId;

      // Load entire map if it exists from firebase
      var array_ref = firebase.database().ref().child('regions').child($stateParams.regionKeyId).child('maps').child($stateParams.mapKeyId).child('zones');
      $scope.zonemap = $firebaseArray(array_ref);

      $scope.zones = [];

      // Load zones from endpoints
        endpoints.post('zones', 'zoneCollectionGet', {'mapKeyId': $stateParams.mapKeyId})
            .then(function(response) {
                // DONE!
                console.log(response);
                $scope.zones = response.zones;

            }, function() {
              // ERROR!
              console.log('error');
            });

        $scope.generateZones = function () {
            endpoints.post('zones', 'fill', {'mapKeyId': $stateParams.mapKeyId}).then(function(resp) {
                  $state.reload();

              });
          }


    }
]);
