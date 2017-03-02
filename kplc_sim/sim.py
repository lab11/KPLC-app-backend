#!/usr/bin/env python

import sched, time, names, random
from dateutil import rrule
from datetime import datetime, timedelta
import sys
import psycopg2
from psycopg2 import errorcodes

try:
    conn=psycopg2.connect("dbname='capstone' user='nklugman' password='gridwatch'")
    print "DB connection"
except Exception,e:
    print e
    print "I am unable to connect to the database."
now = datetime.now()

def gen_consumer():
  hist_range = gen_historical_range()
  historic_data = gen_historic_data(hist_range)
  name = gen_name()
  meter_number = gen_meter_num()
  loc = gen_location()
  consumer ={'name':name, 'meter_number':meter_number, 'loc':loc, 'historical_data':historic_data}
  return consumer

def save_consumers(total_consumers):
  for consumer in total_consumers:
	save_consumer(consumer['name'], consumer['meter_number'], consumer['loc'])
	save_consumer_data(consumer['meter_number'], consumer['name'],consumer['historical_data'])
  print "saving consumers"

def save_consumer_data(meter, name, historic_data):
  print "save_consumer_data"
  cur = conn.cursor()
  try:
   for data_pnt in historic_data:
    balance = data_pnt['balance']
    consumption = data_pnt['consumption']
    time = data_pnt['time'] 
    time_stamp = data_pnt['timestamp'].strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    insert = """INSERT INTO kplc_sim_data(name,meter_num,time,balance,consumption,timestamp) VALUES ("""+"\'"+name+"\',"+str(meter)+","+str(time)+","+str(balance)+","+str(consumption)+",\'"+str(time_stamp)+"\')"
    cur.execute(insert)
    conn.commit()
   cur.close()
  except Exception, e:
    print e
    print "failed to save consumer data"

def save_consumer(name, meter, loc):
  cur = conn.cursor()
  try:
    insert = """INSERT INTO kplc_sim_user(name,meter_num,loc) VALUES ("""+"\'"+name+"\',"+str(meter)+",\'"+str(loc)+"\')"
    cur.execute(insert)
    conn.commit()
    cur.close()
  except Exception, e:
    print e
    print "failed to save consumer"

def gen_historical_range():
  num_days = random.randint(150,400)
  return num_days

def gen_monthly_consumption_coeff():
  consumption_coeff = random.randint(1,5)
  return consumption_coeff

def gen_historic_data(hist_range):
 hundredDaysLater = now + timedelta(days=-hist_range);
 hrly_dist = [1,1,1,1,2,3,4,5,4,3,2,2,2,3,3,4,5,6,7,6,5,4,3,2,1]
 coeff = gen_monthly_consumption_coeff()
 balance = 0
 historical_data = []
 for i,dt in enumerate(rrule.rrule(rrule.HOURLY, dtstart=hundredDaysLater, until=now)):
    noise = random.randint(-coeff/2, coeff/2)
    if (dt.day == 1):
	coeff = gen_monthly_consumption_coeff()
        balance = 0
    consumption = hrly_dist[dt.hour-1] + coeff + noise
    balance += consumption
    cur_data = {'time':dt.strftime('%s'), 'consumption':consumption, 'balance':balance, 'timestamp':dt}
    historical_data.append(cur_data)
 return historical_data

# print 'gen_historic_consumption'
def gen_name():
  name = names.get_first_name();
  return name

def gen_meter_num(): #todo... make sure all are unique
  meter_num = random.randint(1000,2000)
  return meter_num 

def gen_location():
    lat = 19.99
    lon = 73.78
    dec_lat = random.random()/100
    dec_lon = random.random()/100
    return lat+dec_lat, lon+dec_lon    

def create_consumers():
  total_customers = []
  num_consumers = 10
  for consumer in xrange(0,num_consumers):
	total_customers.append(gen_consumer())
  save_consumers(total_customers)

def create_sim():
  reset_sim()
  create_consumers()
  audit_sim()

#clear the data
def reset_sim():
  print 'reset_sim'
  cur = conn.cursor()
  delete = "TRUNCATE kplc_sim_data"
  cur.execute(delete)
  conn.commit()
  delete = "TRUNCATE kplc_sim_user"
  cur.execute(delete)
  conn.commit()
  cur.close()
#check number of users, check that each user has historical data, chek to see that payment tables exist
def audit_sim():
  print 'audit_sim'

##########################3#
# WHILE RUNNING
##########################3#
s = sched.scheduler(time.time, time.sleep)
def run_sim():
    count = 0
    s.enter(1, 1, step_sim, (count,))
    s.run()

def step_sim(sc): 
    print 'updating sim ' + str(sc) 
    sc += 1
    update()
    s.enter(10, 1, step_sim, (sc,))

    #go othrough each consumer and fill in any missiong consumption data

def update():
	#for each user, check the current time of the day
    #fill_gaps()
    
  cur = conn.cursor()
  try:
    get_users = """SELECT name from kplc_sim_user"""
    cur.execute(get_users)
    conn.commit()
    for row in cur.fetchall():
	print row[0]
	get_last_user_date = '''SELECT time, name from kplc_sim_data where name = \''''+row[0]+'\''
	print get_last_user_date 
    cur.close()
  except Exception, e:
    print e
    print "failed to save consumer"

    print 'updating balances for each user'


#lazy but whatever...
if len(sys.argv) == 2:
 if sys.argv[1] == '-c':
   create_sim()
 if sys.argv[1] == '-r':
   reset_sim()
else:
 run_sim()
