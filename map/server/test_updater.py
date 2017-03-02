import shelve
import thread
import socketio
import eventlet
from flask import Flask, render_template
import sched, time, names, random
from dateutil import rrule
from datetime import datetime, timedelta
import sys
import psycopg2
from psycopg2 import errorcodes
import fiona 
import shapely.geometry
import pandas as pd
import requests
import json
import re

#import eventlet
#eventlet.monkey_patch()

#from flask import Flask
#from flask_socketio import SocketIO

#app = Flask(__name__)
#socket = SocketIO(app, logger=True, engineio_logger=True)



d = shelve.open("/home/nklugman/kplc_app/map/server/db/geolocate_cache")

kenya_constituency = fiona.open("../data/shp/constituencies_simplified.shp") #Simplified by QFIS
s = sched.scheduler(time.time, time.sleep)

try:
    conn=psycopg2.connect("dbname='capstone' user='nklugman' password='gridwatch'")
except:
    print "I am unable to connect to the database."
now = datetime.now()

def locate_area_to_shpID(area_list):
    id_list = region_define.region_check(area_list, shapefile)
    return id_list






def geocode(location_string):
        if not d.has_key(str(location_string)):  
	        url = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=AIzaSyAt7_8wh1UsJLJiep7l3jHbmdTJY6bT7wo' % location_string[0]
        	geocode = requests.get(url)
	        geocode = json.loads(geocode.text)
        	latlng_dict = geocode['results'][0]['geometry']['location']
		d[str(location_string)] = [latlng_dict['lat'],latlng_dict['lng']] 
	        return latlng_dict['lat'], latlng_dict['lng']
	else:
		return d[str(location_string)][0],d[str(location_string)][1]

def region_check(area_list, shpfile):
    location_undefined = []
    points_list = []
    effect_area = []
    for area in area_list:
        try:
            points_list.append(geocode(area)) ##(lat, lng)
            effect_area.append(area)
        except IndexError:
            location_undefined.append(area)
    shp_idx = 0
    effect_id = []
    outage_info = []
    for shapefile_rec in shpfile:
        effect_list = []
        count = 0
        for point in points_list:
            this_point = shapely.geometry.Point(point[1],point[0])
            if(shapely.geometry.asShape(shapefile_rec['geometry']).contains(this_point)):
                effect_list.append(effect_area[count])
                if(count not in effect_id):
                    effect_id.append(shp_idx)
            count += 1
        if(len(effect_list)!= 0):
            outage_info.append([shp_idx, len(effect_list), effect_list])
        shp_idx += 1
    new_data=[[obj]for obj in location_undefined]
    return outage_info

def puzzle(wordList,i): #this phrase has i+1 words
    length=len(wordList)
    puzzleList=[]
    for j in range(length//(i+1)):
        phrase=""
        for k in range(i+1):
            phrase=phrase+wordList[i*j+k]+" " #the kth word in the jth phrase
        puzzleList.append(phrase.strip())
    return puzzleList

def parse_tweet(tweet,master_list):
    wordList = re.sub("[^\w]", " ",  tweet).split()
#    wordList = tweet
    words = []
    for word in wordList:
      if word in master_list[0]:
            words.append(word)
    for i in range(1,10):
        puzzleList=puzzle(wordList,i)
        for word in puzzleList:
            if word in master_list[i]:
		words.append(word)
    return words

def build_master_list():
	cur = conn.cursor()
	cur.execute("SELECT area FROM area")
        conn.commit()
	rows = cur.fetchall()
	master_list=[]
	for i in range(11):
	    master_list.append({})
	for row in rows:
	    area=str(row[0]).lower()
	    areaList=area.split()
	    length=len(areaList)
	    master_list[length-1][area]=area
	return master_list

def parse_msg_list(msg_list, master_list):
        '''
	regions = ('central rift', 'coast', 'mt kenya', 'mt. kenya', 'nairobi', 'nairobi north', 'nairobi south', 'nairobi west', 'nairobi eastern', 'north rift',
	'south nyanza', 'western', 'west kenya', 'west')
	for region in regions:
	    areaList=region.split()
	    length=len(areaList)
            master_list[length-1][region]=region
	'''
        total_words = []
        for msg in msg_list:
            cur_words = parse_tweet(msg.lower(),master_list)
            if (not len(cur_words) == 0):
		    total_words.append(cur_words)
	return total_words

def merge_outages(outages):
  merge = {}
  for outage in outages:
	for region in outage['qualified']:
		key = region[0]
		keywords = region[2]
		if key in merge:
			merge[str(key)].append(outage)
		else:
			merge[str(key)] = [outage]
	if outage['service'] == 'a': #coming from the map directly has locality already
		key = outage['shp_idx']
		keyword = outage['shp_idx']
	        if key in merge:
			merge[str(key)].append(outage)
		else:
			merge[str(key)] = [outage]	
  return merge	

def send_update_to_map(update):
  cur = conn.cursor()
  json_update = []
  try:
   for region in update:
	shp_index = region
	cnt = len(update[region]) 
	data = update[region]
  	to_be_json = {}
	to_be_json['cnt'] = cnt
	to_be_json['shp_idx'] = shp_index
	data_str = ""
        for cluster in data:
		data_str += str(cluster) + ","
        data_str = data_str[:-1]
	data_str = data_str.replace("'",'"') 
#	data_str = data_str.replace(",",' ') 
        to_be_json['data'] = data_str
        json_update.append(to_be_json)
   final_update = json.dumps([dict(region=pn) for pn in json_update])
   final_update = final_update.replace("'",'"')
   query = """INSERT INTO update_stream(time, data) values (current_timestamp,\'"""+str(final_update)+"\')"
   cur.execute(query)
   conn.commit()
   cur.close()
  except Exception, e:
    print e
    print "failed to save row"
  print "done"

def get_update():
  master_list = build_master_list()
  print "get_update"
  cur = conn.cursor()
  try:
   interval = 3
   query = "select NULL as shp_idx, time_created as start_time, NULL as end_time, message as msg, 'f' as service from map_test WHERE time_created<= (now()) and time_created>= (now()-INTERVAL '3 hours')"
   cur.execute(query)
   conn.commit()
   rows = cur.fetchall()
   outages = []
   for row in rows:
    try:
     shp_idx = str(row[0])
     start_time = str(row[1])
     end_time = str(row[2])
#     msg = re.sub(r'\W+', '', row[2])
#     msg = msg.replace('"',"'")
     msg = row[3].replace('"',"")
     msg = row[3].replace("'","")
     msg = msg.rstrip('\n')
     service = row[4]
     words = msg.strip().split(" ")
     keywords = parse_msg_list(words, master_list)
     print "\tkeywords: " + str(keywords) 
     qualified_regions = ""
     if not len(keywords) == 0:
       qualified_regions = region_check(keywords, kenya_constituency)      
     print "\tqualified: " + str(qualified_regions) 
     cur_outage = {}
     cur_outage['start_time'] = start_time
     cur_outage['end_time'] = end_time
     cur_outage['msg'] = msg
     cur_outage['service'] = service
     cur_outage['keywords'] = keywords
     cur_outage['qualified'] = qualified_regions
     cur_outage['shp_idx'] = shp_idx
     #print cur_outage
     outages.append(cur_outage)
    except Exception, e:
        print row
	print "Exception: " + str(e) 
    #parse(msg)
   cur.close()
   merged = merge_outages(outages)
   return merged
   #print outages
  except Exception, e:
    print e

#def send_update_to_map(update):
#  for mapable in update:
#	print ""
	#print mapable

def update():
    update = get_update()
    print update
    send_update_to_map(update)



'''
def send_update_to_map(msg):
    socket.emit('update', str(msg))

def listen():
    while True:
        update()
        eventlet.sleep(30)

eventlet.spawn(listen)
'''
if __name__ == '__main__':
    #socket.run(app, host='141.212.11.206')
   update()
#   count = 0
#   s.enter(1, 1, update, (s,count))
#   s.run()


d.close()
