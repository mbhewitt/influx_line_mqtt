from setuptools import setup
setup(
    name="influx_line_mqtt",
    version="0.3.5",
    description="A library to publish data to InfluxDB using MQTT",
    long_description=open("README.md").read(),
    author="Mew Hewitt",
    packages=["influx_line_mqtt"],
    install_requires=["paho-mqtt<2.0",
'influx-line-protocol @ git+https://github.com/mbhewitt/influx-line-protocol#egg=influx-line-protocol'],
)
