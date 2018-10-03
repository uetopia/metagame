var app = angular.module('angular-google-api-example', [
    //'ngCookies',
    'ui.router',
    'angular-google-api-example.router',
    'angular-google-api-example.controller',
    'firebase'

]);

app.constant('AppSettings', {ver: '1.2.2',
                            defaultApiVersion: 'v1',
                            apiUrl: 'https://ue4topia-metagame.appspot.com/_ah/api',
                            //apiUrl: '//localhost:8080/_ah/api',
                            projectName: 'ue4topia-metagame'});

//app.run(['$state', '$rootScope', '$window',  '$http', 'auth', 'session', 'endpoints',
//    function($state, $rootScope, $window,  $http, auth, session, endpoints) {
app.run(['$state', '$rootScope', '$window',  '$http',  'endpoints', '$firebaseObject',
    function($state, $rootScope, $window,  $http,  endpoints, $firebaseObject) {
        //$rootScope.auth = auth;
        //$rootScope.session = session;

        $rootScope.user = null;

        // This is passed into the backend to authenticate the user.
        var userIdToken = null;

        //$http.defaults.headers.common['X-metagame-Auth'] = 'Bearer ' + session.getAccessToken();
        $http.defaults.headers.common['X-metagame-Auth'] = null;

        firebase.auth().onAuthStateChanged(function(user) {
          console.log('onAuthStateChanged')
          if (user) {
            console.log('onAuthStateChanged - user found')
            user.getIdToken().then(function(idToken) {
              userIdToken = idToken;
              $http.defaults.headers.common['X-metagame-Auth'] = 'Bearer ' + userIdToken;
              checkEndpointsAuthentication();

              $rootScope.user = user;

              var ref = firebase.database().ref().child('users').child($rootScope.user.uid);
              $rootScope.userAccount = $firebaseObject(ref);

              $rootScope.userAccount.$loaded(
                function(data) {
                  console.log('userAccount loaded')
                  $rootScope.userAccount_loaded = true;

                }
              )

              // Also look up the active season
              // Leaving this on rootScope even though it's bad practice.
              // Move this to a service if you're doing anything more complex.
              var ref = firebase.database().ref().child('active_season');
              $rootScope.activeSeason = $firebaseObject(ref);


            })

          } else {
            $http.defaults.headers.common['X-metagame-Auth'] = null;
          }
        });

        // [START configureFirebaseLoginWidget]
        // Firebase log-in widget
        configureFirebaseLoginWidget = function() {
          var uiConfig = {
            'signInSuccessUrl': '/',
            callbacks: {
                signInSuccessWithAuthResult: function(currentUser, credential, redirectUrl) {
                    console.log('sign in success');
                    console.log(currentUser);
                    // alert(currentUser)
                    firebase.auth().currentUser.getIdToken(true).then(function(idToken) {
                      console.log('got token');
                      userIdToken = idToken;
                      $http.defaults.headers.common['X-metagame-Auth'] = 'Bearer ' + userIdToken;
                      endpoints.post('users', 'clientSignIn', {})
                          .then(function(response) {
                              // DONE!
                              console.log(response);
                              $window.location.reload();
                              if (response.refresh_token) {
                                console.log('Firebase Unauth - REFRESHING');
                                console.log(firebase.auth());
                              }
                          }, function() {
                            console.log('error');
                          });
                        })
                    return false;
                },
                uiShown: function () {
                    console.log("uiShow");
                }
            },
            'signInOptions': [
              // Leave the lines as is for the providers you want to offer your users.
              firebase.auth.GoogleAuthProvider.PROVIDER_ID,
              //firebase.auth.FacebookAuthProvider.PROVIDER_ID,
              //firebase.auth.TwitterAuthProvider.PROVIDER_ID,
              //firebase.auth.GithubAuthProvider.PROVIDER_ID,
              //firebase.auth.EmailAuthProvider.PROVIDER_ID
            ],
            // Terms of service url
            'tosUrl': '<your-tos-url>',
          };

          var ui = new firebaseui.auth.AuthUI(firebase.auth());
          ui.start('#firebaseui-auth-container', uiConfig);
        }
        // [END configureFirebaseLoginWidget]

        checkEndpointsAuthentication = function() {
          if (userIdToken) {
            endpoints.post('users', 'clientConnect', {})
                .then(function(response) {
                    // DONE!
                    console.log(response);
                    if (response.refresh_token) {
                      console.log('Firebase Unauth - REFRESHING');
                      console.log(firebase.auth());

                    }
                    if (!response.uetopia_connected)
                    {
                      $state.go('uetopiaConnect');
                    }
                }, function() {
                  // ERROR!
                  console.log('error');
                });
          } else {
            console.log('no userIdToken found - skipping');
          }

        };

        // firebase used to call onAuthStateChanged when the token was refreshed, which gave us the chance to update the auth token
        // But, this does not occur anymore.  So we must update and refresh the token manually.
        var authTimerHandle = setInterval(refreshFirebaseToken, 900000); // 15 min

        function refreshFirebaseToken() {
          console.log('refreshing token');
          firebase.auth().currentUser.getIdToken(true).then(function(idToken) {
            console.log('got token');
            userIdToken = idToken;
            $http.defaults.headers.common['X-metagame-Auth'] = 'Bearer ' + userIdToken;
              })
        }


        $rootScope.logout = function() {
          console.log('logout');
            //auth.$unauth();
            firebase.auth().signOut().then(function() {
              // Sign-out successful.
              console.log('Sign-out successful.');
              $rootScope.user = null;
            }, function(error) {
              // An error happened.
              console.log('An error happened.');
            });
        };

        configureFirebaseLoginWidget();
    }
]);
