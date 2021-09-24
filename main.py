import time
import utime
import ubinascii
import pycom
import socket
from pycoproc_2 import Pycoproc
from L76GNSS import L76GNSS
from network import WLAN, LoRa
from struct import *
import Haversine
import bearing

'''
a = [-84.412977,39.152501]
b = [-84.413977,39.152501]
print(Haversine.Haversine(a,b).km)
print(bearing.calculate_initial_compass_bearing(tuple(a),tuple(b)))'''


lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
print("DevEUI:", ubinascii.hexlify(lora.mac()).upper().decode('ascii'))

#energy saving
pycom.heartbeat(False)
pycom.rgbled(0x000000) #off
#wlan = WLAN()
#wlan.deinit() #turn wifi of

py = Pycoproc()
gps = L76GNSS(py)

# Keys
app_eui = ubinascii.unhexlify('0000000000000000') # Replace by your value!
app_key = ubinascii.unhexlify('7C7B8121342A7C6E8C997F6A34B38145') # Replace by your value!
# connect to TTN with retry. You should see "join" requests in the console.
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)
while not lora.has_joined():
    time.sleep(2.5)
    print('Not yet joined...')
print('Joined')
# create a LoRa socket for the communication
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
lat_old = 0;
long_old = 0;
time_old = utime.ticks_ms()/1000.0
while True:
    # make the socket blocking
    # (waits for the data to be sent and for the 2 receive windows to expire)
    s.setblocking(True)

    lat = gps.coordinates()[0]
    long = gps.coordinates()[1]
    time_new = utime.ticks_ms()/1000.0
    if lat_old != 0 and lat_old != None and long_old != 0 and long_old != None and lat != None and long != None:
        pos_old = [lat_old,long_old]
        pos = [lat,long]
        dist = Haversine.Haversine(pos_old,pos).km
        direction = bearing.calculate_initial_compass_bearing(tuple(pos_old),tuple(pos))
        velocity = dist/((time_new-time_old)*3600)
    else:
        dist = None
        direction = None
        velocity = None



    try:
        payload = pack('<ffff',lat,long,direction,velocity)
    except TypeError:
        print("Type Error")
    else:
        print("Payload: " + str(payload) + " Unpacked: " + str(unpack('<ffff',payload)))

        # send some data
        s.send(payload) # You have to change this later to send sensor data
        print("Sent")
    # make the socket non-blocking
    # (because if there’s no data received it will block forever...)
    s.setblocking(False)
    # get any data received (if any...)
    data = s.recv(64)
    if data:
        # data received from TTN. Should be nothing
        print(data)

    lat_old = lat
    long_old = long
    time_old = time_new
    time.sleep(5)# wait some time before sending again.
