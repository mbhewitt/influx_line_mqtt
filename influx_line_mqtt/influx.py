from typing import Any, Dict
import paho.mqtt.client as mqtt
from influx_line_protocol import Metric


class Influx:
    def __init__(self, broker, port: int, topic: str):
        self.client = mqtt.Client()
        self.connect(broker=broker, port=port)
        self.topic = topic

    def connect(self, broker="localhost", port=1883):
        self.client.connect(host=broker, port=port, keepalive=60)
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
        self.client.publish(topic=self.topic, payload=f"[{self.metric}]", qos=1)

    def close(self):
        self.client.loop_stop()
        self.client.disconnect()


# send_data("home/[measurement_type]/","[measurement_type]",["measurement_type":"temp","room":"bed"],[temp:33.0],time.time())
