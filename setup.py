from setuptools import setup
setup(
    name="influx_line_mqtt",
    version="0.3.3",
    description="A library to publish data to InfluxDB using MQTT",
    long_description=open("README.md").read(),
    author="Mew Hewitt",
    packages=["influx_line_mqtt"],
    install_requires=["paho-mqtt","influx-line-protocol"],
)
