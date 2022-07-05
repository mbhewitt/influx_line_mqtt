from typing import Dict, List
import paho.mqtt.client as mqtt


class Influx_Data:
    def __init__(
        self, measurement: str, tag_set: dict, field_set: dict, timestamp: int
    ):
        """A custom object to store data received and decode it in Influx data format

        Args:
            measurement (str)
            tag_set (dict)
            field_set (dict)
            timestamp (int)
        """
        self.measurement = measurement
        self.tag_set = tag_set
        self.field_set = field_set
        self.timestamp = timestamp

    def __str__(self):
        return f"measurement: {self.measurement}\ntag_set: {self.tag_set}\nfield_set: {self.field_set}\ntimestamp: {self.timestamp}"


class Decode:
    def __init__(self, data: str):
        """
        Gives an instance of Decode
        This class is used to decode the message into an instance of Influx_Data class.
        Args:
            data (str): provide the data received by subscriber in influx_line_protocol
        """
        self.data = data.strip()
        self._data_break = self._break()

    def decode(self):
        """
        This message decodes the message and
        returns an instance of Influx Data class.

        """
        return Influx_Data(
            self._measurement(), self._tag_set(), self._field_set(), self._timestamp()
        )

    def _break(self) -> List[str]:
        """Private method to split the data on " "

        Returns:
            List[str]: list of data broken on " "
        """
        return self.data.split(" ")

    def _timestamp(self):
        """Private method to extract the timestamp from the _data_break

        Returns:
            int: timestamp
        """
        return int(self._data_break[2])

    def _field_set(self):
        """Private method to extract the field set from the _data_break
        """
        field_dict = self._data_break[1]
        list_fields = field_dict.split(",")
        field_set = {}
        for field in list_fields:
            if "=" in field:
                field_key = field.split("=")[0]
                field_value = field.split("=")[1]
                field_set[field_key] = field_value

    def _measurement(self):
        """Private method to extract the measurement from the _data_break

        Returns:
            str: measurement
        """
        return self._data_break[0].split(",")[0]

    def _tag_set(self) -> Dict[str, str]:
        """Private method to extract the tag set from the _data_break

        Returns:
            Dict[str,str]: _description_
        """
        list_tags = self._data_break[0].split(",")[1:]
        tag_set = {}
        for tag in list_tags:
            if "=" in tag:
                tag_key = tag.split("=")[0]
                tag_value = tag.split("=")[1]
                tag_set[tag_key] = tag_value

        return tag_set


class Subscriber:
    def __init__(
        self,
        broker: str,
        topic: str,
        port: int = 1883,
        client_id: str = "Smartphone",
    ):
        """Creates an instance of Subscriber.

        Args:
            broker (str): Address of the broker you are using.
            topic (str): Give the topic you want to subscribe to.
            port (int, optional): Port number. Defaults to 1883.
            client_id (str, optional): Client ID. Defaults to "Smartphone".
        """
        self.broker = broker
        self.topic = topic
        self._on_message: function = None
        self.port = port
        self.client = mqtt.Client(client_id)

    @property
    def on_message(self):
        return self._on_message

    @on_message.setter
    def on_message(self, func):
        """property to set the on_message function

        Args:
            func (Callable): Function to be called when message is received
        """
        self._on_message = func

    def start(self):
        """
        Method to start the subscriber to loop forever,
        Before starting please assign on_message
        """
        self.client.connect(self.broker, self.port)
        self.client.subscribe(topic=self.topic)
        self.client.on_message = self._on_message_inner
        self.client.loop_forever()

    def _on_message_inner(self, client, userdata, message):
        """Inner module that takes the received message and decodes it.

        Args:
            client (Any):   MQTT client
            userdata (Any): Userdata
            message (Any): Received message
        """
        message_decode = message.payload.decode("utf-8")
        data: Influx_Data = Decode(message_decode).decode()
        self._on_message(client, userdata, data)
