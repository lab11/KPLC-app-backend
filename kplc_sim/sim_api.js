#!/usr/bin/env node

var express = require('express');
var bodyParser = require('body-parser');
var pg = require('pg')
var con_string = 'tcp://nklugman:gridwatch@localhost:5432/capstone';
var app = express();

app.get('/check_balance', function (req, res) {
  console.log("check_balance");
});

app.get('/pay_balance', function (req, res) {
  console.log("pay_balance");
});

app.get('/check_consumption', function (req, res) {
  console.log("check_consumption");
});

var server = app.listen(3122, "141.212.11.206", function () {
  console.log('Server on localhost listening on port 3111');
});

