# Wemo Lightswitch Control via MQTT

This is a python script that bridges between a Wemo light switch and an MQTT broker

* Topic: "lighting/porchlight"
* Commands "On/Off/Status"

## Install:

* Install dependencies at the top of the python file
* Set your IP address to the Wemo switch
* Adapt mqtt_porchlight.service to match your user an file location
  * Copy mqtt_porchlight.service to /etc/systemd/system folder
  * `systemctl enable mqtt_porchlight.service`
  * `systemctl start mqtt_porchlight.service`

## Todo:

* Add ability to schedule via MQTT
