import time
import ubinascii
import pycom
import socket
from pycoproc_2 import Pycoproc
from L76GNSS import L76GNSS
from network import WLAN, LoRa
from struct import *


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
while True:
    # make the socket blocking
    # (waits for the data to be sent and for the 2 receive windows to expire)
    s.setblocking(True)

    payload = pack('<ff',gps.coordinates()[0],gps.coordinates()[1])
    print("Payload: " + str(payload) + " Unpacked: " + str(unpack('<ff',payload)))

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

    time.sleep(30)# wait some time before sending again.
