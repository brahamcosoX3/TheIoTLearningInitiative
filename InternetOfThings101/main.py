#!/usr/bin/python

import paho.mqtt.client as paho
import psutil
import pywapi
import signal
import sys
import time
import dweepy

from threading import Thread
from flask import Flask
from flask_restful import Api, Resource

import plotly.plotly as py
from plotly.graph_objs import Scatter, Layout, Figure

import pyupm_i2clcd as lcd
import pyupm_grove as grove

myLcd = lcd.Jhd1313m1(0, 0x3E, 0x62)
myLcd.setColor(255, 255, 255)

light = grove.GroveLight(0)


app = Flask(__name__)
api = Api(app)


class Network(Resource):
    def get(self):
        data = 'Network Data: %i' % dataNetwork()
        return data

username = 'brahamcosoX3'
api_key = '2no5uo7af9'
stream_token = 'npg3mqqj85'

def interruptHandler(signal, frame):
    sys.exit(0)

def on_publish(mosq, obj, msg):
    pass

def dataNetwork():
    netdata = psutil.net_io_counters()
    return netdata.packets_sent + netdata.packets_recv

def getmac(interface):
    try:
        mac = open('/sys/class/net/' + interface + '/address').readline()
    except:
        mac = "00:00:00:00:00:00"
    return mac[0:17]

def dataNetworkHandler():
    idDevice = "Charles: " + getmac("wlan0")
    mqttclient = paho.Client()
    mqttclient.on_publish = on_publish
    mqttclient.connect("test.mosquitto.org", 1883, 60)
    while True:
        packets = dataNetwork()
        message = idDevice + " " + str(packets)
        #print "MQTT dataNetworkHandler " + message
        mqttclient.publish("IoT101/Network", message)
        time.sleep(1)

def on_message(mosq, obj, msg):
    print "MQTT dataMessageHandler %s %s" % (msg.topic, msg.payload)

def dataMessageHandler():
    mqttclient = paho.Client()
    mqttclient.on_message = on_message
    mqttclient.connect("test.mosquitto.org", 1883, 60)
    mqttclient.subscribe("IoT101/Message", 0)
    while mqttclient.loop() == 0:
        pass

def dataWeatherHandler():
    weather = pywapi.get_weather_from_weather_com('MXJO0043', 'metric')
    message = "Weather Report in " + weather['location']['name']
    message = message + ", Temperature "
    message = message + (weather['current_conditions']['temperature'] + " C")
    message = message + ", Atmospheric Pressure "
    message = message + (weather['current_conditions']
            ['barometer']['reading'][:-3] + " mbar")
    dataLcd = "%s-%s C, %s mbar" % ( weather['location']['name'], weather['current_conditions']['temperature'],weather['current_conditions']['barometer']['reading'][:-3])
    #print message
    return dataLcd

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
    print py.plot(fig, filename = 'Hello Internet of Things 101 Plotly')
    i = 0
    stream = py.Stream(stream_token)
    stream.open()
    while True:
        stream_data = dataPlotly()
        stream.write({'x': i, 'y': stream_data})
        i += 1
        time.sleep(0.25)


api.add_resource(Network, '/network')

if __name__ == '__main__':

    signal.signal(signal.SIGINT, interruptHandler)

    threadx = Thread(target=dataNetworkHandler)
    threadx.start()

    thready = Thread(target=dataMessageHandler)
    thready.start()

    threadz = Thread(target=dataPlotlyHandler)
    threadz.start()

    app.run(host='0.0.0.0', debug=True)

    while True:
        myLcd.setCursor(0, 0)
        toString = dataWeatherHandler()
        a,b = toString.split("-")
        myLcd.write(str(a))
        myLcd.setCursor(1, 0)
        myLcd.write(str(b))
        dweepy.dweet_for('brahamcosoIoT101', {'value': str(light.value())})
        time.sleep(5)

# End of File
