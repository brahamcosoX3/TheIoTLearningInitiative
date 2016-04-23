#!/usr/bin/python

import psutil
import signal
import sys
import time

from threading import Thread

def interruptHandler(signal, frame):
    sys.exit(0)

def dataNetwork():
    netdata = psutil.net_io_counters()
    return netdata.packets_sent + netdata.packets_recv

def dataNetworkHandler():
    idDevice = "IoT101Device"
    while True:
        packets = dataNetwork()
        message = idDevice + " " + str(packets)
        print "dataNetworkHandler " + message
        time.sleep(1)

if __name__ == '__main__':

    signal.signal(signal.SIGINT, interruptHandler)

    threadx = Thread(target=dataNetworkHandler)
    threadx.start()

    while True:
        print "Hello Internet of Things 101"
        time.sleep(5)

# End of File
