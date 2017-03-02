#!/usr/bin/env node

//Adding module
var express = require('express'); 
var mustacheExpress = require('mustache-express'); 
var bodyParser = require('body-parser');
var pg = require('pg')
//var conString = "postgres://postgres:gridwatch@localhost:5432/gridwatch";
var conString = "postgres://nklugman:gridwatch@localhost:5432/capstone";
//Initialize
var app = express();

app.get('/newsfeed', function (req, res) {
  console.log("newsfeed");

    var time = req.query.time;

    var client = new pg.Client(conString);
    
    client.connect();
    var queryExpr;
    console.log(time);
    if (!time || time == "null") {
      queryExpr = "SELECT * From news_feed";
    } else {
      queryExpr = "SELECT * From news_feed where time > \'" + time +"\'";
    }
    var query = client.query(queryExpr);
    query.on("row", function (row, result) {
         result.addRow(row);
    });
    query.on("end", function (result) {
        
     // On end JSONify and write the results to console and to HTML output
     console.log(JSON.stringify(result.rows, null, "    "));
        res.writeHead(200, {'Content-Type': 'text/plain'});
        res.write(JSON.stringify(result.rows) + "\n");
        res.end();
     });

});
app.get('/postpaid', function (req, res) {
  console.log("postpaid");

    var date = req.query.date;
    var account = req.query.account;
    var client = new pg.Client(conString);
    client.connect();
    var queryExpr;
    if (!date || date == "null") {
      queryExpr = "SELECT * From postpaid where account = \'" + account+"\'";
    } else {
      queryExpr = "SELECT * From postpaid where month > \'" + date +"\'and account = \'" + account +"\'";
    }
    console.log(queryExpr);
    var query = client.query(queryExpr);
    query.on("row", function (row, result) {
         result.addRow(row);
    });
    query.on("end", function (result) {
        
     // On end JSONify and write the results to console and to HTML output
     console.log(JSON.stringify(result.rows, null, "    "));
        res.writeHead(200, {'Content-Type': 'text/plain'});
        res.write(JSON.stringify(result.rows) + "\n");
        res.end();
     });
  

});

process.on('uncaughtException', (err) => {
  console.log('whoops! there was an error', err.stack);
});
// Start up server on port 3000 on host localhost
var server = app.listen(3100, "141.212.11.206", function () {
  console.log('Server on localhost listening on port 3100');
});
