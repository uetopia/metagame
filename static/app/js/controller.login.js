var controller = angular.module('angular-google-api-example.controller.login', []);

controller.controller('angular-google-api-example.controller.login', ['$scope','$state',
    function clientList($scope, $state) {


      $scope.doLogin = function() {

          // login with Google
            auth.logIn()
          //    console.log("Firebase: Signed in as:", firebaseUser.user.uid);
          //    console.log('test');
          //    accessToken = firebaseUser.credential.accessToken;
          //    idToken = firebaseUser.credential.idToken;


          //    ifLogin();
          //  }).catch(function(error) {
          //    console.log("Authentication failed:", error);
          //  });
        };



    }
])
