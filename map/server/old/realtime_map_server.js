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

var con_string = 'tcp://nklugman:gridwatch@localhost:5432/nklugman';
//var pg_client = new pg.Client(con_string);
//pg_client.connect();

pg.connect(con_string, function(err, client) {
  if(err) {
    console.log(err);
  }
  socket.on('connection', function(client){ 
    console.log('Connection to client established');
    client.on('message',function(event){ 
        console.log('Received message from client!',event);
    });
    client.on('disconnect',function(){
        console.log('Server has disconnected');
    });
  });

   
  client.on('notification', function(msg) {
    console.log(msg); 
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
  var query = client.query("LISTEN addedrecord");
});



//var query = pg_client.query('LISTEN addedrecord');

/*
*/
