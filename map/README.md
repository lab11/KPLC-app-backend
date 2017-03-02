Map Server
==========

This process currently does a little more than its named to do and should eventually split into multiple servers.

The maps server reads from the aggregate event table and presents events over a
SocketIO stream to the KPLC outage map. The outage map itself is simply a webview
in the app (can also view in broweser).

The webpage for the outage map is currently served by symlinking the `/map/map.html`
file from this repo to a live Apache site. Eventually it probably makes sense for
this server to serve that page as well.
