var controller = angular.module('angular-google-api-example.controller.region.detail', []);

controller.controller('angular-google-api-example.controller.region.detail', ['$scope', '$state', 'endpoints','$stateParams','$firebaseArray',
    function regionCreateCtl($scope, $state, endpoints, $stateParams, $firebaseArray) {

      $scope.regionKeyId = $stateParams.regionKeyId;
      $scope.maps = [];

      // Load maps from firebase
      // Load entire map if it exists from firebase
      var array_ref = firebase.database().ref().child('regions').child($stateParams.regionKeyId).child('maps');
      $scope.maps = $firebaseArray(array_ref);


    }
]);
