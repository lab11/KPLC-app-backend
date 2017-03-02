var bodyParser = require('body-parser')
var request = require('request')
var fs = require('fs');
var http = require('http');
var https = require('https');
var privateKey  = fs.readFileSync('sslcert/privkey.pem', 'utf8');
var certificate = fs.readFileSync('sslcert/fullchain.pem', 'utf8');

var credentials = {key: privateKey, cert: certificate};
var express = require('express');
var app = express();
var httpsServer = https.createServer(credentials, app);
httpsServer.listen(3112)


// Process application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({extended: false}))

// Process application/json
app.use(bodyParser.json())

app.get('/',function(req,res){
        if (req.query['hub.verify_token'] === 'gridwatch') {
        res.send(req.query['hub.challenge'])
        }
        res.send('wrong token,error'
                 )
        })


app.get('/webhook',function(req,res){
        if (req.query['hub.verify_token'] === 'gridwatch') {
        res.send(req.query['hub.challenge'])
        }
        res.send('wrong token,error'
                 )
        })



