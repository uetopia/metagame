var controller = angular.module('angular-google-api-example.controller.map.detail', []);

controller.controller('angular-google-api-example.controller.map.detail', ['$scope', '$state', 'endpoints','$stateParams','$firebaseArray','$firebaseObject',
    function regionCreateCtl($scope, $state, endpoints, $stateParams, $firebaseArray, $firebaseObject) {

      $scope.regionKeyId = $stateParams.regionKeyId;
      $scope.mapKeyId = $stateParams.mapKeyId;

      // Load the map from firebase
      var mapref = firebase.database().ref().child('regions').child($stateParams.regionKeyId).child('maps').child($stateParams.mapKeyId);
        $scope.map = $firebaseObject(mapref);

      // Load entire map if it exists from firebase
      var array_ref = firebase.database().ref().child('regions').child($stateParams.regionKeyId).child('maps').child($stateParams.mapKeyId).child('zones');
      $scope.zonemap = $firebaseArray(array_ref);


      // submitBid(zone)
      $scope.submitBid = function(zone) {
        zone.zoneKeyId = zone.key_id;
              endpoints.post('zones', 'zoneBid', zone
                                                          ).then(function(resp) {
                  console.log(resp.response_message);
                    console.log(resp);
                    alert(resp.response_message);
                });
            }




    }
]);
