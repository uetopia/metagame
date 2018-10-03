(function (angular) {

  function fbModels($firebaseArray) {
    // create a reference to the database location where we will store our data
    var ref = firebase.database().ref().child("model");

    // this uses AngularFire to create the synchronized array
    return $firebaseArray(ref);
  }

  // Inject dependencies
  fbModels.$inject = ['$firebaseArray'];

  // Export
  angular
    .module('angular-google-api-example')
    .factory('fbModels', fbModels);

})(angular);
