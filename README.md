# Wemo Lightswitch Control via MQTT

This is a python script that bridges between a Wemo light switch and an MQTT broker

- Topic: "lighting/porchlight"
- Commands "On/Off/Status"

## Install:

- Install dependencies:

    ```
    pip install -r requirements.txt
    ```
- Set your IP address to the Wemo switch

### MQTT broker

This script connects to an MQTT broker (default: `192.168.1.135:1883`,
set in `wemo-mqtt-control.py`). If you don't already run one, install
mosquitto on the same or another machine:

```
sudo apt install mosquitto mosquitto-clients
```

The script connects without a username or password, so the broker must
permit anonymous connections. Mosquitto 2.x rejects anonymous clients
by default; create `/etc/mosquitto/conf.d/local.conf`:

```
listener 1883
allow_anonymous true
```

Then restart and verify:

```
sudo systemctl restart mosquitto
mosquitto_sub -h 127.0.0.1 -t 'lighting/porchlight/#' -v
```

If your broker requires authentication, add credentials in
`wemo-mqtt-control.py` before `connect()`:

```python
client.username_pw_set("username", "password")
```

### systemd service

- Adapt mqtt_porchlight.service to match your user and file location
  - Copy mqtt_porchlight.service to /etc/systemd/system folder
  - `systemctl enable mqtt_porchlight.service`
  - `systemctl start mqtt_porchlight.service`

## Todo:

* Add ability to schedule via MQTT
