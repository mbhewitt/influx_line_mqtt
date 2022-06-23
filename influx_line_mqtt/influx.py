import time
from typing import Any, Dict, List
import paho.mqtt.client as mqtt
from influx_line_protocol import Metric


class Influx:
    def __init__(self, broker, port: int, topic: str):
        self.client = mqtt.Client("Temperature_Sensor")
        self.connect(broker=broker, port=port)
        self.topic = topic

    def connect(self, broker="localhost", port=1883):
        self.client.connect(host=broker, port=port)
        self.client.loop_start()

    def make_data(
        self,
        dest_table: str,
        tags: Dict[str, Any],
        values: Dict[str, Any],
        epoch_timestamp: float,
    ):
        self.metric = Metric(dest_table)
        self.metric.with_timestamp(epoch_timestamp * 1000000000)

        for (k, v) in values.items():
            self.metric.add_value(k, v)
        for (k, v) in tags.items():
            self.metric.add_tag(k, v)

    def send_data(self):
        print(f'Sent data: {self.metric}')
        self.client.publish(topic=self.topic, payload=f"[{self.metric}]")

    def close(self):
        self.client.loop_stop()
        self.client.disconnect()
        
if __name__ == "__main__":
    broker = "mqtt.eclipseprojects.io"
    port = 1883

    inf = Influx(broker=broker,port=port, topic="test778")
    while True:
        inf.make_data(
        dest_table= "[measurement_type]",
        tags={"measurement_type":"temp","room":"bed"},
        values={"temp":33.0},
        epoch_timestamp= time.time())
        inf.send_data()
        time.sleep(5)

# send_data("home/[measurement_type]/","[measurement_type]",["measurement_type":"temp","room":"bed"],[temp:33.0],time.time())
