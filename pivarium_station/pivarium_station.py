import Adafruit_DHT

SENSORTYPE_HUMIDITY_TEMP = Adafruit_DHT.DHT22
PIN_HUMIDITY_TEMP = 4

while True:
    humidity, temp = Adafruit_DHT.read_retry(SENSORTYPE_HUMIDITY_TEMP, PIN_HUMIDITY_TEMP)
    if humidity is not None and temp is not None:
        print("Temp={0:0.1f}*C Humidity={1:0.1f}%".format(temp, humidity))
    else:
        print("Failed to retrieve data")
