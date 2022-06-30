from setuptools import setup
setup(
    name="influx_line_mqtt",
    version="0.2.0",
    description="A library to publish data to InfluxDB using MQTT",
    long_description=open("readme.txt").read(),
    author="Priyam Srivastava",
    packages=["influx_line_mqtt"],
    install_requires=["paho-mqtt","influx-line-protocol"],
)
