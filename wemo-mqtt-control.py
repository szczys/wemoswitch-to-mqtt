#!/usr/bin/python3

#Install dependancy:
#sudo pip3 install pywemo
#sudo pip3 install paho-mqtt
#sudo pip3 install schedule
#sudo pip3 install astral

import pywemo
import paho.mqtt.client as mqtt
import schedule
import time
import datetime
from astral import Astral


mqtt_broker_addr = "192.168.1.135"
porchlight_addr = "192.168.1.137"
topic_base = "lighting/porchlight"
topic_cmd = topic_base + "/control"
topic_status = topic_base + "/status"
topic_schedule = topic_status + "/schedule"
city = "Madison"


#Wemo functions

#Don't use discovery, count on IP addresses
#FIXME: What happens if switch is not found?
port = pywemo.ouimeaux_device.probe_wemo(porchlight_addr)
url = 'http://%s:%i/setup.xml' % (porchlight_addr, port)
porchlight = pywemo.discovery.device_from_description(url, None)

def wemo_changestate(client,state):
    if state=="On":
        porchlight.on()
        publish_status(client)
    elif state=="Off":
        porchlight.off()
        publish_status(client)

#MQTT functions
def publish_status(client):
    client.publish(topic_status, retain=True, payload="Status:%s:%s" % (porchlight.name,("Off","On")[porchlight.get_state()]))


def on_connect(client, userdata, flags, rc):
    connect_report = "Wemo %s: %s" % (porchlight.device_type,porchlight.name)
    print(connect_report)
    client.subscribe(topic_cmd)
    client.publish(topic_status, payload = connect_report)
    publish_status(client)
    

def on_message(client, userdata, msg):
    try:
        cmd = msg.payload.decode()
    except:
        return

    if (cmd == "On") or (cmd == "Off"):
        print("Setting state to: %s" % cmd)
        wemo_changestate(client,cmd)
    elif (cmd == "Status"):
        publish_status(client)

#Scheduled task functions
def service_sundown(client):
    #Update any schedules with "sundown" in them to match daily changes
    #this should be run every day mid-day
    #print("sundown schedule running")
    sundown_events = [x for x in schedule.jobs if "sundown" in x.tags]
    for event in sundown_events:
        #print(event)
        n = event.next_run
        newsundown = get_sundown(n)
        event.next_run = datetime.datetime(n.year, n.month, n.day, newsundown.hour, newsundown.minute)
        event.at_time = datetime.time(newsundown.hour, newsundown.minute)
        client.publish(topic_schedule, retain=True, qos=1, payload="Next sundown set for: %s" % event.next_run.strftime("%H:%M"))

def get_sundown(target_date):
    a = Astral()
    a.solar_depression = 'civil'
    locale = a[city]
    sun = locale.sun(date=datetime.date(target_date.year,target_date.month,target_date.day), local=True)
    return sun['sunset']

#Setup MQTT Client
client = mqtt.Client()
client.connect(mqtt_broker_addr,1883,60)
client.on_connect = on_connect
client.on_message = on_message
#Start the MQTT thread that handles this client
client.loop_start()

#Do the scheduling
#FIXME: This should be user setable
schedule.every().day.at("16:30").do(porchlight.on).tag("sundown")
schedule.every().day.at("05:30").do(porchlight.off)
#Schedule the sundown time updater and kickstart it for the first time
schedule.every().day.at("12:01").do(service_sundown,client).tag("sundownscheduler")
service_sundown(client)

#Use 1 Hz loop to handle scheduling
while(True):
    schedule.run_pending()
    time.sleep(60)
