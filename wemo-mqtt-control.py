#!/usr/bin/python3

#Install dependancy:
#sudo pip3 install pywemo
#sudo pip3 install paho-mqtt
#sudo pip3 install schedule

import pywemo
import paho.mqtt.client as mqtt
import schedule
import time
import datetime

porchlight_addr = "192.168.1.137"
topic = "lighting/porchlight"


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
    client.publish(topic, payload="Status:%s:%s" % (porchlight.name,("Off","On")[porchlight.get_state()]))


def on_connect(client, userdata, flags, rc):
    connect_report = "Wemo %s: %s" % (porchlight.device_type,porchlight.name)
    print(connect_report)
    client.subscribe(topic)
    client.publish(topic, payload = connect_report)
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
    print("sundown schedule running")
    newhour = 19
    newminute = 21
    sundown_events = [x for x in schedule.jobs if "sundown" in x.tags]
    for event in sundown_events:
        print(event)
        n = event.next_run
        event.next_run = datetime.datetime(n.year, n.month, n.day, newhour, newminute)
        event.at_time = datetime.time(newhour, newminute)
        client.publish(topic, payload="Next sundown set for: %s" % event.next_run.strftime("%H:%M"))

#Setup MQTT Client
client = mqtt.Client()
client.connect("RaspberryPi",1883,60)
client.on_connect = on_connect
client.on_message = on_message
#Start the MQTT thread that handles this client
client.loop_start()

#Do the scheduleing
#FIXME: This should be user setable
schedule.every().day.at("16:30").do(porchlight.on).tag("sundown")
schedule.every().day.at("23:00").do(porchlight.off)
#Schedule the sundown time updater
schedule.every().day.at("16:42").do(service_sundown,client).tag("sundownscheduler")

#Use 1 Hz loop to handle scheduling
while(True):
    schedule.run_pending()
    time.sleep(1)
