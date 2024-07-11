"""
Micropython IOT Weather logging project
To view the data:

1. Go to http://www.hivemq.com/demos/websocket-client/
2. Click "Connect"
3. Under Subscriptions, click "Add New Topic Subscription"
4. In the Topic field, type "wokwi-weather" then click "Subscribe"

Now click on the DHT22 sensor in the simulation,
change the temperature/humidity, and you should see
the message appear on the MQTT Broker, in the "Messages" pane.

"""

import network
import time
import machine 
from machine import Pin,
import dht
import ujson
from umqtt.simple import MQTTClient

# MQTT Server Parameters
MQTT_CLIENT_ID = "micropython-weather-demo"
MQTT_BROKER    = "broker.mqttdashboard.com"
MQTT_USER      = ""
MQTT_PASSWORD  = ""
MQTT_TOPIC     = "wokwi-weather"

def connect_and_publish():
    try:
        client.connect()
        client.publish(MQTT_TOPIC, message)
    except OSError as e:
        print('Connection error:', e)
        time.sleep(5)
        reconnect()

def reconnect():
    global client
    while True:
        try:
            client.connect()
            print('Reconnected')
            break
        except OSError as e:
            print('Reconnection failed:', e)
            time.sleep(5)

sensor = dht.DHT22(Pin(15))
led    = Pin(2,Pin.OUT)

print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')
while not sta_if.isconnected():
  print(".", end="")
  time.sleep(0.1)
print(" Connected!")

print("Connecting to MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD,keepalive=60)
client.connect()

print("Connected!")

prev_weather = ""
while True:
  print("Measuring weather conditions... ", end="")
  sensor.measure() 
  message = ujson.dumps({
    "temperature": sensor.temperature(),
    "humidity": sensor.humidity(),
  })
  if message != prev_weather:
    print("Updated!")
    led.value(1)
    time.sleep(1)
    led.value(0)
    time.sleep(1)
    print("Reporting to MQTT topic {}: {}".format(MQTT_TOPIC, message))
    connect_and_publish()
    prev_weather = message
  else:
    print("No change in weather conditions.")
  time.sleep(5)

