#!/usr/bin/python3

#Install dependancy:
#sudo pip3 install pywemo
#sudo pip3 install paho-mqtt

import pywemo
import paho.mqtt.client as mqtt

porchlight_addr = "192.168.1.137"
topic = "lighting/porchlight"



#Don't use discovery, count on IP addresses
port = pywemo.ouimeaux_device.probe_wemo(porchlight_addr)
url = 'http://%s:%i/setup.xml' % (porchlight_addr, port)
porchlight = pywemo.discovery.device_from_description(url, None)


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

    if (cmd == "On"):
        print("Setting state to: On")
        porchlight.on()
        publish_status(client)
    elif (cmd == "Off"):
        print("Setting state to: Off")
        porchlight.off()
        publish_status(client)
    elif (cmd == "Status"):
        publish_status(client)


client = mqtt.Client()
client.connect("RaspberryPi",1883,60)
client.on_connect = on_connect
client.on_message = on_message
client.loop_forever()
