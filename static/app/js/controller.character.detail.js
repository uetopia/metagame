var controller = angular.module('angular-google-api-example.controller.character.detail', []);

controller.controller('angular-google-api-example.controller.character.detail', ['$scope', '$state', 'endpoints','$stateParams',
    function regionCreateCtl($scope, $state, endpoints, $stateParams) {

      $scope.characterKeyId = $stateParams.characterKeyId;
      $scope.active_season_key_id = 0;
      $scope.seasonCharacters = {};
      $scope.achievements = {};
      $scope.season_achievements = {};

      // get the character
      endpoints.post('characters', 'get', {'key_id': $stateParams.characterKeyId})
            .then(function(response) {
                // DONE!
                console.log(response);
                $scope.character = response;

                $scope.character.kdratio = ($scope.character.kills / $scope.character.deaths).toFixed(2);
                $scope.character.winratio = ($scope.character.matches_won / ($scope.character.matches_played - $scope.character.matches_won) ).toFixed(2);
                // calculate averages
                $scope.character.damage_dealt_avg = ($scope.character.damage_dealt / $scope.character.matches_played).toFixed(2);
                //$scope.character.healing_dealt_avg = ($scope.character.healing_dealt / $scope.character.matches_played).toFixed(2);
                $scope.character.damage_received_avg = ($scope.character.damage_received / $scope.character.matches_played).toFixed(2);
                //$scope.character.healing_received = ($scope.character.healing_received / $scope.character.matches_played).toFixed(2);

                $scope.character.kills_avg = ($scope.character.kills / $scope.character.matches_played).toFixed(2);
                $scope.character.deaths_avg = ($scope.character.deaths / $scope.character.matches_played).toFixed(2);
                $scope.character.assists_avg = ($scope.character.assists / $scope.character.matches_played).toFixed(2);


                // the season characters are in here too.
                $scope.seasonCharacters = response.season_characters;

                // the active season key id is in here too.
                $scope.active_season_key_id = response.active_season_key_id;


                //  Get achievements and seasonal achievements
                // Load achievements
                $scope.postargs = {};
                $scope.postargs.characterKeyId = $scope.character.key_id;
                $scope.postargs.awarded = true;

                endpoints.post('achievements', 'progressCollectionGet', $scope.postargs)
                    .then(function(response) {
                        // DONE!
                        console.log(response);
                        $scope.achievements = response.achievement_progrogresses;
                    }, function() {
                      // ERROR!
                      console.log('error');
                    });

                $scope.postargs.seasonKeyId = $scope.active_season_key_id;

                endpoints.post('achievements', 'seasonProgressCollectionGet', $scope.postargs)
                    .then(function(response) {
                        // DONE!
                        console.log(response);
                        $scope.season_achievements = response.achievement_progrogresses;
                    }, function() {
                      // ERROR!
                      console.log('error');
                    });


                endpoints.post('matches', 'mmmatchCharacterCollectionGet', $scope.postargs)
                    .then(function(response) {
                        // DONE!
                        console.log(response);
                        $scope.matches = response.mm_match_characters;
                    }, function() {
                      // ERROR!
                      console.log('error');
                    });


                //$state.go('home');
            }, function() {
              // ERROR!
              console.log('error');
            });


    }
]);
