"use strict";angular.module("localApp",["ngAnimate","ngAria","ngCookies","ngMessages","ngResource","ngRoute","ngSanitize","ngTouch"]).config(["$routeProvider",function(a){a.when("/",{templateUrl:"views/paradrop-settings.html",controller:"ParadropSettingsCtrl"}).when("/paradrop-settings",{redirectTo:"/"}).when("/internet-status",{templateUrl:"views/internet-status.html",controller:"InternetStatusCtrl"}).otherwise({redirectTo:"/"})}]),angular.module("localApp").controller("ParadropSettingsCtrl",[function(){}]),angular.module("localApp").controller("InternetStatusCtrl",[function(){}]),angular.module("localApp").run(["$templateCache",function(a){a.put("views/internet-status.html","<p>This is the about view.</p>"),a.put("views/paradrop-settings.html",'<div class="jumbotron"> <h1>\'Allo, \'Allo!</h1> <p class="lead"> <img src="images/yeoman.8cb970fb.png" alt="I\'m Yeoman"><br> Always a pleasure scaffolding your apps. </p> <p><a class="btn btn-lg btn-success" ng-href="#/">Splendid!<span class="glyphicon glyphicon-ok"></span></a></p> </div> <div class="row marketing"> <h4>HTML5 Boilerplate</h4> <p> HTML5 Boilerplate is a professional front-end template for building fast, robust, and adaptable web apps or sites. </p> <h4>Angular</h4> <p> AngularJS is a toolset for building the framework most suited to your application development. </p> <h4>Karma</h4> <p>Spectacular Test Runner for JavaScript.</p> </div>')}]);