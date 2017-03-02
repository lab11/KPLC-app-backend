#!/usr/bin/env python
import shelve
import urllib
import lxml.html
import time

d = shelve.open("/home/nklugman/kplc_app/data/scheduled_outages/db/scheduled_outages")
log = open('/home/nklugman/kplc_app/data/scheduled_outages/log/outage_scraping_log', 'a')
log.write("ran " + time.ctime() + "\n")
to_download = [];

def check_interruptions_page():
  connection = urllib.urlopen('http://kplc.co.ke/category/view/50/power-interruptions')
  dom =  lxml.html.fromstring(connection.read())
  for link in dom.xpath('//a/@href'): # select the url in href for all a tags(links)
    if "interruptions---" in link:
	raw_link = link
	format_link = link.split("/")[-1]
	if format_link[-1] == "-":
		format_link = format_link[:-1]
	split_link = format_link.split("---")
	link_type = split_link[0]
	link_date = split_link[1]
	if not d.has_key(link_date):
		meta_data = {}
		meta_data['name'] = link_date
		meta_data['type'] = link_type
		meta_data['link'] = str(raw_link)
		meta_data['access'] = time.ctime()
		to_download.append(meta_data)

def download():
  for download_item in to_download:
	link = download_item['link']
	filename = download_item['name']
	link_type = download_item['type']
	con = urllib.urlopen(link)
	dom = lxml.html.fromstring(con.read())
	for link in dom.xpath('//a/@href'):
		if ".pdf" in link:
			localDestination = "/home/nklugman/kplc_app/data/scheduled_outages/pdfs/" +filename+".pdf"
			resultFilePath, responseHeaders = urllib.urlretrieve(link, localDestination)
			if responseHeaders['Content-Type'] == 'application/pdf':
				download_item['local_path'] = localDestination	
				d[filename] = download_item
				print "added " + str(download_item) 
				log.write("\t"+str(download_item) + "\n")
			else:
				print "failed to download at: " + link
				log.write("\t Failed to download at: " + link + "\n")

check_interruptions_page();
if not len(to_download) == 0:
  download()
d.close()
