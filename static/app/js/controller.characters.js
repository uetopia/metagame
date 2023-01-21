var controller = angular.module('angular-google-api-example.controller.characters', []);

controller.controller('angular-google-api-example.controller.characters', ['$scope', '$state', 'endpoints','$stateParams','$firebaseArray','$firebaseObject',
    function regionCreateCtl($scope, $state, endpoints, $stateParams, $firebaseArray, $firebaseObject) {


      // Load the characters from firebase
      var charactersref = firebase.database().ref().child('characters');
        $scope.characters = $firebaseArray(charactersref);



    }
]);
