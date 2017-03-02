Data Pull
=========

Each of these is responsible for pulling data from different sources.

Each utility writes data into its own table. The separate aggregator
(`/map/server/updater.py` as of this writing) process collects all of
the data sources into an aggregate table for apps to consume.
