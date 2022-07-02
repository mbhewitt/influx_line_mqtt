import contextlib
import time
from typing import Any, Dict, List
import paho.mqtt.client as mqtt
from influx_line_protocol import Metric
import datetime


class Client:
    def __init__(self, broker: str, port: int,client_id:str="Random"):
        """Create an instance of Influx

        Args:
            broker (str):Address of the broker you are using
            port (int): port number you want to connect on
            client_id (str): Client id 
        """
        self.client = mqtt.Client(client_id)
        self._connect(broker=broker, port=port)

    def _connect(self, broker="localhost", port=1883):
        self.client.connect(host=broker, port=port)
        self.client.loop_start()

    def _fix_dest_table(self, dest_table: str, tags):
        if dest_table is None:
            dest_table = f"{list(tags.values())[0]}"
        return dest_table

    def _fix_topic(self, topic: str, tags: Dict[str, Any]):
        for value in tags.values():
            topic = f"{topic}/{value}"
        return f"{topic}/"

    def _fix_timestamp(self, epoch_timestamp: float):
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
    
    def make_send(self,
        topic: str,
        tags: Dict[str, Any],
        values: Dict[str, Any],
        epoch_timestamp: float,
        dest_table: str | None = None,                  
                  ):
        """Method to make data and send it
        """
        self._make_data(
            topic=topic,
            tags=tags,
            values=values,
            epoch_timestamp=epoch_timestamp,
            dest_table=dest_table,
        )
        self._send_data()
        

    def _make_data(
        self,
        topic: str,
        tags: Dict[str, Any],
        values: Dict[str, Any],
        epoch_timestamp: float,
        dest_table: str | None = None,
    ):
        """
        Use this method to make data and encode it in influx_line_protocol
        data is stored in metric.

        Args:
            topic (str): Add the topic of the message
            tags (Dict[str, Any]): Tags you would like to send. 
            values (Dict[str, Any]): values you would like to add
            epoch_timestamp (float): Timestamp you would like to define defaults to now.
            dest_table (str | None, optional): Dest_table you would like to add. Defaults to None.
        """
        dest_table = self._fix_dest_table(dest_table, tags)
        self.topic = self._fix_topic(topic, tags)
        self.metric = Metric(dest_table)
        self.metric.with_timestamp(self._fix_timestamp(epoch_timestamp))
        for (k, v) in values.items():
            self.metric.add_value(k, v)
        for (k, v) in tags.items():
            self.metric.add_tag(k, v)

    def _send_data(self):
        """Method to sent the made data made after using_make_data 
        """
        self.client.publish(topic=self.topic, payload=f"{self.metric}")

    def close(self):
        self.client.loop_stop()
        self.client.disconnect()


if __name__ == "__main__":
    
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

