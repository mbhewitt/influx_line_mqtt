from pydoc import cli
import paho.mqtt.client as mqtt


def on_message(client, userdata, message):
    print("Message Received: ", message.payload.decode("utf-8"))

mqttBroker = "mqtt.eclipseprojects.io"
client = mqtt.Client("Smartphone")
client.connect(mqttBroker, 1883)
client.subscribe("test778")
client.on_message = on_message

client.loop_forever()

