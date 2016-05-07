#!/usr/bin/python

# Libraries
import paho.mqtt.client as paho
import psutil
import pywapi
import signal
import sys
import time
import dweepy
import random

import plotly.plotly as py
import pyupm_i2clcd as lcd
import pyupm_grove as grove

from threading import Thread
from flask import Flask
from flask_restful import Api, Resource
from plotly.graph_objs import Scatter, Layout, Figure
from Adafruit_IO import MQTTClient


# Global variables
# Display config
myLcd = lcd.Jhd1313m1(0, 0x3E, 0x62)
myLcd.setColor(255, 255, 255)

# Light sensor config
light = grove.GroveLight(0)

# Relay
relay = grove.GroveRelay(4)

# Restful init
#app = Flask(__name__)
#api = Api(app)

# Adafruit variables
ADAFRUIT_IO_KEY      = 'cd6bfee245bd4b2c9e14fe2eb882643a'
ADAFRUIT_IO_USERNAME = 'brahamcoso'

# Plotly variables
username = 'brahamcosoX3'
api_key = '2no5uo7af9'
stream_token = 'npg3mqqj85'

# Classes
class Network(Resource):
    def get(self):
        data = 'Network Data: %i' % dataNetwork()
        return data


# Functions
def interruptHandler(signal, frame):
    sys.exit(0)

def on_publish(mosq, obj, msg):
    pass

def dataNetwork():
    netdata = psutil.net_io_counters()
    return netdata.packets_sent + netdata.packets_recv

def getMac(interface):
    try:
        mac = open('/sys/class/net/' + interface + 
'/address').readline()
    except:
        mac = "00:00:00:00:00:00"
    return mac[0:17]

def dataWeatherHandler():
    weather = pywapi.get_weather_from_weather_com('MXJO0043', 'metric')
    message = "Weather Report in " + weather['location']['name']
    message = message + ", Temperature "
    message = message + (weather['current_conditions']['temperature'] + 
" C")
    message = message + ", Atmospheric Pressure "
    message = message + (weather['current_conditions']
            ['barometer']['reading'][:-3] + " mbar")
    dataLcd = "%s-%s C, %s mbar" % ( weather['location']['name'], 
weather['current_conditions']['temperature'],weather['current_conditions']['barometer']['reading'][:-3])
    #print message
    return dataLcd

def connected(client):
    print 'Connected to Adafruit IO!  Listening for DemoFeed changes...'
    client.subscribe('my-data')

def disconnected(client):
    print 'Disconnected from Adafruit IO!'
    sys.exit(1)

def message(client, feed_id, payload):
    print 'Feed {0} received new value: {1}'.format(feed_id, payload)


# Network Thread
def dataAdafruitHandler():
    client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

    client.on_connect    = connected
    client.on_disconnect = disconnected
    client.on_message    = message

    client.connect()
    client.loop_background()
    while True:
        value = random.randint(0, 100)
        print 'Publishing {0} to my-data.'.format(value)
        client.publish('my-data', value)
        time.sleep(5)

# Network Thread
def dataNetworkHandler():
    idDevice = "Charles: " + getMac("wlan0")
    while True:
        packets = dataNetwork()
        message = idDevice + " " + str(packets)
        #print "MQTT dataNetworkHandler " + message
        mqttclient.publish("IoT101/Network", message)
        time.sleep(2)

# Message Thread
def on_message(mosq, obj, msg):
    print "MQTT dataMessageHandler %s %s" % (msg.topic, msg.payload)
    if "78:4b:87:9f:39:35/Actuator" in msg.topic:
        if msg.payload == '1':
            relay.on()
        elif msg.payload == '0':
            relay.off()

def dataMessageHandler():
    mqttclient.subscribe("IoT101/#", 0)
    #mqttclient.subscribe("IoT101/78:4b:87:9f:39:35/Actuator", 0)
    while mqttclient.loop() == 0:
        pass

# Plotly Thread
def dataPlotly():
    return dataNetwork()

def dataPlotlyHandler():
    py.sign_in(username, api_key)
    trace1 = Scatter(
        x=[],
        y=[],
        stream = dict(
            token = stream_token,
            maxpoints = 200))

    layout = Layout(
        title='Hello Internet of Things 101 Data')
    fig = Figure(data = [trace1], layout = layout)
    print py.plot(fig, filename = 'Hello Internet of Things 101 Plotly', auto_open=False)
    i = 0
    stream = py.Stream(stream_token)
    stream.open()
    while True:
        stream_data = dataPlotly()
        stream.write({'x': i, 'y': stream_data})
        i += 1
        time.sleep(0.25)

# Light Thread
def dataLightHandler():
    while True:
        dweepy.dweet_for('brahamcosoIoT101',
                {'value': str(light.value())})
	time.sleep(2)


#api.add_resource(Network, '/network')


if __name__ == '__main__':

    signal.signal(signal.SIGINT, interruptHandler)

# Mosquitto config
    mqttclient = paho.Client()
    mqttclient.on_publish = on_publish
    mqttclient.on_message = on_message
    mqttclient.connect("test.mosquitto.org", 1883, 60)

# Run Restful site
    #app.run(host='0.0.0.0', debug=True)


# Threads
    threadv = Thread(target=dataAdafruitHandler)
    threadv.start()

    threadw = Thread(target=dataLightHandler)
    threadw.start()
	
    threadx = Thread(target=dataNetworkHandler)
    threadx.start()

    thready = Thread(target=dataMessageHandler)
    thready.start()

    threadz = Thread(target=dataPlotlyHandler)
    threadz.start()

    while True:
        myLcd.setCursor(0, 0)
        toString = dataWeatherHandler()
        a,b = toString.split("-")
        myLcd.write(str(a))
        myLcd.setCursor(1, 0)
        myLcd.write(str(b))
        time.sleep(5)

# End of File
