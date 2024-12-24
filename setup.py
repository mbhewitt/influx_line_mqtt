from setuptools import setup
setup(
    name="influx_line_mqtt",
    version="0.3.5",
    description="A library to publish data to InfluxDB using MQTT",
    long_description=open("README.md").read(),
    author="Mew Hewitt",
    packages=["influx_line_mqtt"],
    install_requires=["paho-mqtt<2.0",
'influx_line_protocol @ git+https://github.com/mbhewitt/influx_line_protocol#egg=/influx_line_protocol'],
)
