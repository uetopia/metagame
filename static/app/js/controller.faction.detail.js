var controller = angular.module('angular-google-api-example.controller.faction.detail', []);

controller.controller('angular-google-api-example.controller.faction.detail', ['$scope', '$state', 'endpoints','$stateParams','$firebaseArray','$firebaseObject',
    function regionCreateCtl($scope, $state, endpoints, $stateParams, $firebaseArray, $firebaseObject) {

      $scope.factionKeyId = $stateParams.factionKeyId;

      // Load the faction from firebase
      var factionref = firebase.database().ref().child('factions').child($stateParams.factionKeyId);
        $scope.faction = $firebaseObject(factionref);

      // Load controlled zones from firebase
      var array_ref = firebase.database().ref().child('factions').child($stateParams.factionKeyId).child('zones');
      $scope.zones = $firebaseArray(array_ref);

    }
]);
