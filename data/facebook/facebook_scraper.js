var FB = require('fb'); /* facebook */
var fs = require('fs'); /* node's built-in filesystem library */
var pg = require ('pg'); /* postgres */
var con_string = 'tcp://nklugman:gridwatch@localhost:5432/capstone';
var client = new pg.Client(con_string);

// JSON file of the form:
// {
//     client_id: '...',
//     client_secret: '...',
//     grant_type: '...'
// }
var facebook_credentials = JSON.parse(fs.readFileSync('./facebook_credentials_SECRET.json'));


setTimeout(function(){ process.exit(1); }, 5000);

FB.api('oauth/access_token', facebook_credentials, function (res) {
    if(!res || res.error) {
        console.log(!res ? 'error occurred' : res.error);
        return;
    }
    var accessToken = res.access_token;
    FB.setAccessToken(accessToken);
    FB.api(
	  '/KenyaPowerLtd/feed',
	  'GET',
	  {},
	  function(response) {
		 pg.connect(con_string, function(err, client, done) {
		   for (var i = 0; i < response.data.length; i++) {
     		     cur_post = response.data[i];
                     if (cur_post.message == null) {
			return
 		     }
		     console.log(cur_post);
			client.query(
				'INSERT INTO facebook_stream (facebook_id, message, time_created, time_accessed) SELECT $1, $2, $3, current_timestamp WHERE NOT EXISTS (SELECT 1 FROM facebook_stream WHERE message LIKE $4)', 
				[cur_post.id, cur_post.message, cur_post.created_time, cur_post.message],
			function(err, result){
			if (err) {
			        console.log('err');
				console.log(err);
			} else {
				console.log(result);
			}});
		  }
            });
   });
});

