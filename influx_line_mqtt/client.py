import contextlib
from typing import Any, Dict
import paho.mqtt.client as mqtt
from influx_line_protocol import Metric
import datetime


class Client:
    def __init__(self, broker: str, port: int, client_id: str = "Random",qos=2):
        """Create an instance of Client

        Args:
            broker (str):Address of the broker you are using
            port (int): port number you want to connect on
            client_id (str): Client id 
        """
        self.client = mqtt.Client(client_id)
        self._connect(broker=broker, port=port)
        self.qos=qos

    def _connect(self, broker="localhost", port=1883):
        """Private method to connect to the broker and start loop for sending data

        Args:
            broker (str, optional): the broker id. Defaults to "localhost".
            port (int, optional): port number. Defaults to 1883.
        """
        self.client.connect(host=broker, port=port)
        self.client.loop_start()

    def _fix_dest_table(self, dest_table: str, tags) -> str:
        """Private method to extract the dest_table from the tags if it is not defined

        Args:
            dest_table (str): original dest_table sent by user in make_send or _make_data.
            tags (_type_): tags sent by user in make_send or _make_data.

        Returns:
            (str): _description_
        """
        if dest_table is None:
            dest_table = f"{list(tags.values())[0]}"
        return dest_table

    def _fix_topic(self, topic: str, tags: Dict[str, Any]) -> str:
        """Private method to extract the topic from the tags and append it to original topic

        Args:
            topic (str): topic sent by user in make_send or _make_data.
            tags (Dict[str, Any]): tags sent by user in make_send or _make_data.

        Returns:
            (str): Fixed topic
        """
        return topic

    def _fix_timestamp(self, epoch_timestamp) -> float:
        """
        Private method to fix the timestamp
        and standardize it to the format of influx_line_protocol.


        Args:
            epoch_timestamp (float|str|Datetime): Timestamp you would like to define defaults to now.

        Returns:
            (float): Timestamp in the format of influx_line_protocol.
        """

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
                  dest_table: str,
                  ):
        """
        Use this method to make data and encode it in influx_line_protocol
        data is stored in metric and send it to the broker.

        Args:
            topic (str): Add the topic of the message
            tags (Dict[str, Any]): Tags you would like to send. 
            values (Dict[str, Any]): values you would like to add
            epoch_timestamp (float): Timestamp you would like to define defaults to now.
            dest_table (str | None, optional): Dest_table you would like to add. Defaults to None.
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
        dest_table: str,
    ):
        """
        Private method to make data and encode it in influx_line_protocol
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
        self.client.publish(topic=self.topic, payload=f"{self.metric}",qos=self.qos)

    def close(self):
        """
        Method to close the connection to the broker
        and stop the loop
        """
        self.client.loop_stop()
        self.client.disconnect()
