import contextlib
import time
from typing import Any, Dict, List
import DateTime
import paho.mqtt.client as mqtt
from influx_line_protocol import Metric
import datetime


class Influx:
    def __init__(self, broker, port: int):
        self.client = mqtt.Client("Temperature_Sensor")
        self.connect(broker=broker, port=port)

    def connect(self, broker="localhost", port=1883):
        self.client.connect(host=broker, port=port)
        self.client.loop_start()

    def fix_dest_table(self, dest_table: str, tags):
        if dest_table is None:
            dest_table = f"{list(tags.values())[0]}"
        return dest_table

    def fix_topic(self, topic: str, tags: Dict[str, Any]):
        for value in tags.values():
            topic = f"{topic}/{value}"
        return f"{topic}/"

    def fix_timestamp(self, epoch_timestamp: float):
        if isinstance(epoch_timestamp, datetime.datetime):
            epoch_timestamp = epoch_timestamp.timestamp()
        if type(epoch_timestamp) is float:
            epoch_timestamp = epoch_timestamp * 10**9
        else:
            with contextlib.suppress(Exception):
                epoch_timestamp = (
                    datetime.datetime.strptime(
                        epoch_timestamp, "%Y-%m-%d %H:%M:%S.%f"
                    ).timestamp()
                    * 10**9
                )
                return epoch_timestamp
            try:
                epoch_timestamp = (
                    datetime.datetime.strptime(
                        epoch_timestamp, "%Y-%m-%d %H:%M:%S"
                    ).timestamp()
                    * 10**9
                )
                return epoch_timestamp
            except Exception:
                print(
                    f"{epoch_timestamp} is not a valid timestamp \nThe correct format is YYYY-MM-DD HH:MM:SS.SSS\nPlease try this or use a datetime object"
                )
                exit()
        return epoch_timestamp

    def make_data(
        self,
        topic: str,
        tags: Dict[str, Any],
        values: Dict[str, Any],
        epoch_timestamp: float,
        dest_table: str | None = None,
    ):
        dest_table = self.fix_dest_table(dest_table, tags)
        self.topic = self.fix_topic(topic, tags)
        self.metric = Metric(dest_table)
        self.metric.with_timestamp(self.fix_timestamp(epoch_timestamp))
        for (k, v) in values.items():
            self.metric.add_value(k, v)
        for (k, v) in tags.items():
            self.metric.add_tag(k, v)

    def send_data(self):
        print(f"Sent data: {self.topic} -> {self.metric}")
        self.client.publish(topic=self.topic, payload=f"{self.metric}")

    def close(self):
        self.client.loop_stop()
        self.client.disconnect()


if __name__ == "__main__":
    broker = "mqtt.eclipseprojects.io"
    port = 1883

    inf = Influx(broker=broker, port=port)
    while True:
        inf.make_data(
            topic="home",
            tags={"measurement_type": "temp", "room": "bed"},
            values={"temp": 33.0},
            epoch_timestamp="2022-06-24 16:06:25.126144",
        )
        inf.send_data()
        time.sleep(5)

# send_data("home/[measurement_type]/","[measurement_type]",["measurement_type":"temp","room":"bed"],[temp:33.0],time.time())
# 2022-06-24 16:06:25.126144
