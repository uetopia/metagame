var router = angular.module('angular-google-api-example.router', []);

router
    .config(['$urlRouterProvider',
        function($urlRouterProvider) {
            $urlRouterProvider.otherwise("/");
        }]);

router
    .config(['$stateProvider',
        function($stateProvider) {

            $stateProvider

                .state('home', {
                    url :'/',
                    views :  {
                        '': {
                            controller: 'angular-google-api-example.controller.home',
                            templateUrl: '/app/partials/home.html',
                        },
                    },
                })

                .state('uetopiaConnect', {
                    url :'/uetopia/connect',
                    views :  {
                        '': {
                            controller: 'angular-google-api-example.controller.uetopia.connect',
                            templateUrl: '/app/partials/uetopia.connect.html',
                        },
                    },
                })

                .state('regionDetail', {
                    url :'/regions/:regionKeyId',
                    views :  {
                        '': {
                            controller: 'angular-google-api-example.controller.region.detail',
                            templateUrl: '/app/partials/region.detail.html',
                        },
                    },
                })

                .state('mapDetail', {
                    url :'/region/:regionKeyId/maps/:mapKeyId',
                    views :  {
                        '': {
                            controller: 'angular-google-api-example.controller.map.detail',
                            templateUrl: '/app/partials/map.detail.html',
                        },
                    },
                })

                .state('characters', {
                    url :'/characters/',
                    views :  {
                        '': {
                            controller: 'angular-google-api-example.controller.characters',
                            templateUrl: '/app/partials/characters.html',
                        },
                    },
                })

                .state('characterDetail', {
                    url :'/characters/:characterKeyId',
                    views :  {
                        '': {
                            controller: 'angular-google-api-example.controller.character.detail',
                            templateUrl: '/app/partials/character.detail.html',
                        },
                    },
                })

                .state('matchDetail', {
                    url :'/matches/:matchKeyId',
                    views :  {
                        '': {
                            controller: 'angular-google-api-example.controller.match.detail',
                            templateUrl: '/app/partials/match.detail.html',
                        },
                    },
                })

                .state('edit', {
                    url :'/edit/{id}',
                    views :  {
                        '': {
                            controller: 'angular-google-api-example.controller.edit',
                            templateUrl: '/app/partials/edit.html',
                        },
                    },
                })

                // ADMIN

                .state('adminHome', {
                    url :'/admin/',
                    views :  {
                        '': {
                            controller: 'angular-google-api-example.controller.admin.home',
                            templateUrl: '/app/partials/admin/home.html',
                        },
                    },
                })

                .state('adminRegionCreate', {
                    url :'/admin/region_create',
                    views :  {
                        '': {
                            controller: 'angular-google-api-example.controller.admin.region.create',
                            templateUrl: '/app/partials/admin/region.create.html',
                        },
                    },
                })

                .state('adminRegionDetail', {
                    url :'/admin/region/:regionKeyId',
                    views :  {
                        '': {
                            controller: 'angular-google-api-example.controller.admin.region.detail',
                            templateUrl: '/app/partials/admin/region.detail.html',
                        },
                    },
                })



                .state('adminSeasonCreate', {
                    url :'/admin/season_create',
                    views :  {
                        '': {
                            controller: 'angular-google-api-example.controller.admin.season.create',
                            templateUrl: '/app/partials/admin/season.create.html',
                        },
                    },
                })

                .state('adminSeasonDetail', {
                    url :'/admin/season/:seasonKeyId',
                    views :  {
                        '': {
                            controller:'angular-google-api-example.controller.admin.season.detail',
                            templateUrl: '/app/partials/admin/season.detail.html',
                        },
                    },
                })




                .state('adminMapCreate', {
                    url :'/admin/map_create',
                    views :  {
                        '': {
                            controller: 'angular-google-api-example.controller.admin.map.create',
                            templateUrl: '/app/partials/admin/map.create.html',
                        },
                    },
                })

                .state('adminMapDetail', {
                    url :'/admin/region/:regionKeyId/maps/:mapKeyId',
                    views :  {
                        '': {
                            controller: 'angular-google-api-example.controller.admin.map.detail',
                            templateUrl: '/app/partials/admin/map.detail.html',
                        },
                    },
                })

                .state('adminAchievementCreate', {
                    url :'/admin/achievement_create',
                    views :  {
                        '': {
                            controller: 'angular-google-api-example.controller.admin.achievement.create',
                            templateUrl: '/app/partials/admin/achievement.create.html',
                        },
                    },
                })

                .state('adminAchievementDetail', {
                    url :'/admin/achievements/:achievementKeyId',
                    views :  {
                        '': {
                            controller: 'angular-google-api-example.controller.admin.achievement.detail',
                            templateUrl: '/app/partials/admin/achievement.detail.html',
                        },
                    },
                })


                // FACTIONS
                .state('factionDetail', {
                    url :'/factions/:factionKeyId',
                    views :  {
                        '': {
                            controller: 'angular-google-api-example.controller.faction.detail',
                            templateUrl: '/app/partials/faction.detail.html',
                        },
                    },
                })







    }])
