# Wemo Lightswitch Control via MQTT

This is a python script that bridges between a Wemo light switch and an MQTT broker

- Topic: "lighting/porchlight"
- Commands "On/Off/Status"

## Install:

- Set your IP address to the Wemo switch

### Python environment (uv)

Install [uv](https://docs.astral.sh/uv/).

Create the virtual environment and install dependencies:

```
uv venv
uv pip install -r requirements.txt
```

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

**Before installing the service, edit `mqtt_porchlight.service` to match
your system: set `User=` to your username and update `WorkingDirectory=`/
`ExecStart=` to point at your checkout.** (systemd's `%h` specifier cannot
be used here: in system units it expands against the systemd manager's
user, which is root, not the `User=` set in the unit.)

The service runs `run.sh`, which resolves the repo directory and
executes `.venv/bin/python` from it, so the virtualenv created above
must exist before the service starts.

- Edit User= and paths in mqtt_porchlight.service to match your system
  - Copy mqtt_porchlight.service to /etc/systemd/system folder
  - `systemctl daemon-reload`
  - `systemctl enable mqtt_porchlight.service`
  - `systemctl start mqtt_porchlight.service`

## Todo:

* Add ability to schedule via MQTT
