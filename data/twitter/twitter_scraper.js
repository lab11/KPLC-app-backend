#!/usr/bin/env node

var fs = require ('fs');
var pg = require ('pg');
var con_string = 'tcp://nklugman:gridwatch@localhost:5432/capstone';
var client = new pg.Client(con_string);

// JSON file of the form:
// {
//   consumer_key: "...",
//   consumer_secret: "...",
//   access_token_key: "...",
//   access_token_secret: "..."
// }
var twitter_credentials = JSON.parse(fs.readFileSync('./twitter_credentials_SECRET.json'));

var possible_locs = ["Turkana","Marsabit","Mandera","Wajir", "West Pokot", "Samburu", "Isiolo", "Baringo", "Keiyo-Marakwet", "Trans Nzoia", "Bungoma", "Garissa", "Uasin Gishu", "Kakamega", "Laikipia", "Busia", "Meru", "Nandi", "Siaya", "Nakuru", "Vihiga", "Nyandarua", "Tharaka", "Kericho", "Kisumu", "Nyeri", "Tana River", "Kitui", "Kirinyaga", "Embu", "Homa Bay", "Bomet", "Nyamira", "Narok", "Kisii", "Murang'a", "Migori", "Kiambu", "Machakos", "Kajiado", "Nairobi", "Makueni", "Lamu", "Kilifi", "Taita Taveta", "Kwale", "Mombasa" ];
var Twitter = require('twitter');
var client = new Twitter(twitter_credentials);

function aContainsB (a, b) {
    return a.toLowerCase().indexOf(b.toLowerCase()) >= 0;
}


var stream = client.stream('statuses/filter', {track: 'kplc,kenya power,KenyaPower_Care,KenyaPower,GridWatch,Kenya Power'});//['kplc', 'kenya power', 'KenyaPower_Care', 'KenyaPower', 'gridwatch']});
stream.on('data', function(event) {

  /*
  console.log(event.text)
  for (var i = 0; i < possible_locs.length; i++) {
	if (aContainsB(event.text, possible_locs[i])) {
		console.log(possible_locs[i]);
	}	
  }
  */
  pg.connect(con_string, function(err, client, done) {
        client.query(
 		'INSERT INTO twitter_stream(id, id_str, text, source, truncated, in_reply_to_status_id, in_reply_to_status_id_str, in_reply_to_user_id, in_reply_to_user_id_str, in_reply_to_screen_name, twitter_user, geo, coordinates, place, contributors, is_quote_status, retweet_count, favorite_count, entities, favorited, retweeted, filter_level, timestamp_ms, lang, time_accessed) values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, to_timestamp($23), $24, current_timestamp)',[event.id, event.id_str, event.text, event.source, event.truncated, event.in_reply_to_status_id,  event.in_reply_to_status_id_str, event.in_reply_to_user_id, event.in_reply_to_user_id_str, event.in_reply_to_screen_name, event.user, event.geo, event.coordinates, event.place, event.contributors, event.is_quote_status, event.retweet_count, event.favorite_count, event.entities, event.favorited, event.retweeted, event.filter_level, Math.floor(event.timestamp_ms/1000), event.lang],
            function(err, result) {
                if (err) {
                    console.log(err);
                } else {
                    console.log('row inserted');
                }
                client.end();
            });        
  });
});
 
stream.on('error', function(error) {
  throw error;
});
 
