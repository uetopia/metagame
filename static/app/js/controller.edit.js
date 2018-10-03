var controller = angular.module('angular-google-api-example.controller.edit', []);

controller.controller('angular-google-api-example.controller.edit', ['$scope',  '$state', '$stateParams', '$filter', 'fbModels', 'endpoints',
    function homeCtl($scope, $state, $stateParams, $filter, fbModels, endpoints) {
      //console.log(fbModels);
      $scope.model = $filter('filter')(fbModels, function (d) {return d.key_id === $stateParams.id;})[0];
      //$scope.model = $stateParams;
      //$scope.model.name = $stateParams.name;
      //console.log($scope.model);

    	$scope.submitEdit = function() {
        $state.go('home');
        endpoints.post('seed', 'modelUpdate', {key_id: $scope.model.key_id, name: $scope.model.name, description: $scope.model.description})
            .then(function(response) {
                // DONE!
                console.log(response);
                if (response.response_message === "Firebase Unauth.") {
                  console.log('Firebase Unauth');

                  //auth.refreshtoken();
                }
                //$state.go('home');
            }, function() {
              // ERROR!
              console.log('error');
            });

    	}
    }
]);
