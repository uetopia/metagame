var controller = angular.module('angular-google-api-example.controller.match.detail', []);

controller.controller('angular-google-api-example.controller.match.detail', ['$scope', '$state', 'endpoints','$stateParams',
    function regionCreateCtl($scope, $state, endpoints, $stateParams) {

      $scope.matchKeyId = $stateParams.matchKeyId;

      $scope.active_season_key_id = 0;
      $scope.matchCharacters = {};
      $scope.winningTeam = {};
      $scope.losingTeam = {};
      $scope.matchStoryLines = [];


      // get the character
      endpoints.post('matches', 'get', {'key_id': $stateParams.matchKeyId})
            .then(function(response) {
                // DONE!
                console.log(response);
                $scope.match = response;

                $scope.matchStoryLines = $scope.match.description.split('<br/>');
                $scope.matchStoryLines.pop(); // remove last = empty
                console.log($scope.matchStoryLines);

                // the player data is in the match

                $scope.winningTeam = $scope.match.winningTeam;
                $scope.losingTeam = $scope.match.losingTeam;

                //$state.go('home');
            }, function() {
              // ERROR!
              console.log('error');
            });


    }
]);
