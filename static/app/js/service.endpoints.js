(function (angular) {

  function EndpointsApiService($q, $http, AppSettings) {

    var createEndpointUrl = function(service, endpoint, version) {
        version = version || AppSettings.defaultApiVersion;
        endpoint = endpoint.replace('.', '/');
        return [
          AppSettings.apiUrl,
          //AppSettings.projectName,
          service,
          version,
          endpoint
        ].join('/');
    };

    this.get = function(service, endpoint, args, version) {
      var deferred = $q.defer();

      $http({url: createEndpointUrl(service, endpoint, version), method: "GET", params: args}).success(function(data) {
          deferred.resolve(data);
      }).error(function(err, status) {
          deferred.reject(err, status);
      });

      return deferred.promise;
    };

    this.post = function(service, endpoint, args, version) {
      var deferred = $q.defer();

      $http.post(createEndpointUrl(service, endpoint, version), args).success(function(data) {
          deferred.resolve(data);
      }).error(function(err, status) {
          deferred.reject(err, status);
      });

      return deferred.promise;
    };

  }

  // Inject dependencies
  EndpointsApiService.$inject = ['$q', '$http', 'AppSettings'];

  // Export
  angular.module('angular-google-api-example')
    .service('endpoints', EndpointsApiService);

})(angular);
