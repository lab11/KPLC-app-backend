SSL Certs
=========

The Facebook API requires https. Letsencrypt does most of the heavy lifting,
but once you've got things set up, you'll need two symlinks here, looking
something like this:

```
fullchain.pem -> /etc/letsencrypt/live/graphs.grid.watch/fullchain.pem
privkey.pem -> /etc/letsencrypt/live/graphs.grid.watch/privkey.pem
```

TODO: Add some documention for how to set up / run letsencrypt for this
application here.
