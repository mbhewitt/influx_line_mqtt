# inlfux_line_mqtt

This package enables an easy interface for using **[influx_data_protocol](https://docs.influxdata.com/influxdb/v2.3/reference/syntax/line-protocol/)** with **[mqtt client](https://mqtt.org/).**

This module provides with interface for both client-publisher and subscriber

### Install

`git clone https://github.com/mbhewitt/inlfux_line_mqtt `

`cd influx_line_mqtt`

`pip install dist/influx_line_mqtt-0.3.1-py3-none-any.whl`

##### To use client-publisher

```
from inlfux_line_mqtt.client import Client

broker = "mqtt.eclipseprojects.io"
port = 1883
inf = Client(broker=broker, port=port)
while True:
      inf.make_send(
            topic="home",
            tags={"measurement_type": "temp", "room": "bed"},
            values={"temp": 33.0},
            epoch_timestamp="2022-06-24 16:06:25.126144",
       )
       time.sleep(5)
```

##### To use subsciber

```
from influx_line_mqtt.subscriber import Subscriber

def pp(client, userdata, data):
    print(data)

mqttBroker = "mqtt.eclipseprojects.io"
sub = Subscriber(mqttBroker, "home/temp/bed/", port=1883)
sub.on_message = pp
sub.start()
```
