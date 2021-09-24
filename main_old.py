'''import time
import pycom
import machine
from network import LoRa
import ubinascii
import socket

from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE

from pycoproc_2 import Pycoproc

from struct import *


pycom.heartbeat(False)
pycom.rgbled(0x0A0A08) # white

lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

py = Pycoproc()
if py.read_product_id() != Pycoproc.USB_PID_PYSENSE:
    raise Exception('Not a Pysense')

print("DevEUI:", ubinascii.hexlify(lora.mac()).upper().decode('ascii'))

alt = MPL3115A2(py, mode=ALTITUDE) # Returns height in meters. Mode may also be set to PRESSURE, returning a value in Pascals
print("MPL3115A2 temperature: " + str(alt.temperature()))
print("Altitude: " + str(alt.altitude()))
pres = MPL3115A2(py,mode=PRESSURE) # Returns pressure in Pa. Mode may also be set to ALTITUDE, returning a value in meters
print("Pressure: " + str(pres.pressure()))

dht = SI7006A20(py)
print("Temperature: " + str(dht.temperature())+ " deg C and Relative Humidity: " + str(dht.humidity()) + " %RH")
print("Dew point: "+ str(dht.dew_point()) + " deg C")

# Read out the accelerometer
acc = LIS2HH12(py)
print("Acceleration: " + str(acc.acceleration()))
print(pack('fff',acc.acceleration()[0],acc.acceleration()[1],acc.acceleration()[2]))

# Keys
app_eui = ubinascii.unhexlify('0000000000000000') # Replace by your value!
app_key = ubinascii.unhexlify('13E72A4351D19ED9DA24425068E58EB8') # Replace by your value!
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

    # Read out the accelerometer
    acc = LIS2HH12(py)
    print("Acceleration: " + str(acc.acceleration()))
    payload = pack('<fff',acc.acceleration()[0],acc.acceleration()[1],acc.acceleration()[2])
    print("Payload: " + str(payload))

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
    '''
