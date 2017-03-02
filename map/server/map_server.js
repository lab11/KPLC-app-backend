#!/usr/bin/env node

var pg = require ('pg');
var io = require('socket.io')
var http = require('http');
var port = 9000

var server = http.createServer(function(req, res){ 
    res.writeHead(200,{ 'Content-Type': 'text/html' }); 
    res.end('<h1>Hello Socket Lover!</h1>');
});
server.listen(port);
var socket = io.listen(server);

var con_string = 'tcp://nklugman:gridwatch@localhost:5432/capstone';
var pg_client = new pg.Client(con_string);
pg_client.connect();

pg.connect(con_string, function(err, client) {
  if(err) {
    console.log(err);
  }
  socket.on('connection', function(client){ 
    console.log('Connection to client established');
    client.on('upvote',function(event){ 
        console.log('Received message from client!',event);
    });
    client.on('disconnect',function(){
        console.log('Server has disconnected');
    });
    client.on('vote',function(client){
	console.log(client)
       var direction = client['direction'];
       var shp_idx = client['shp_idx'];
       var note = client['note'];
       if (note != 'Enter (optional) notes here.') {
		console.log('real')
       } else {
	note = '';
       }
       var query_text = 'INSERT INTO direct_report_stream (shp_idx, msg, time, entry_point, direction) values (\''+shp_idx+'\',\''+note+'\',now(),\'map\',\''+direction+'\')';
       console.log(query_text);
       pg_client.query(query_text, function(err, result) {
         if(err) {console.log(err);}//handle error
         else {
         }
       });
       console.log('upvoting');
    });
  });



  client.on('notification', function(msg) {
    //console.log(msg); 
    socket.emit('update',msg);
    /* 
      socket.emit('connected', { connected: true });
      socket.on('ready for data', function (data) {
        pg_client.on('notification', function(title) {
    console.log(msg);
            socket.emit('update', { msg });
        });
    });
    */
  });
  var query = client.query("LISTEN update");
});



//var query = pg_client.query('LISTEN addedrecord');

/*
*/
