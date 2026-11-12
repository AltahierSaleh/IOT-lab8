import network
import time
from machine import Pin
import umqtt.robust as umqtt
from config import WIFI_SSID, WIFI_PASSWORD, HOSTNAME

PORT = 1883
TOPIC = "temp/pico"

led = Pin("LED", Pin.OUT)
led.off()

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASSWORD)

for attempt in range(30):
    if wlan.isconnected():
        break
    print("Connecting to Wi-Fi...")
    time.sleep(1)
else:
    raise RuntimeError("Wi-Fi connection failed. Check the hotspot and config.py.")

print("Connected to Wi-Fi:", wlan.ifconfig()[0])

def callback(topic, message):
    if topic != TOPIC.encode():
        return
    temp = float(message.decode())
    print("Received temperature:", round(temp, 2), "C")
    if temp > 25:
        led.on()
    else:
        led.off()

mqtt = umqtt.MQTTClient(
    client_id=b"subscriber",
    server=HOSTNAME.encode(),
    port=PORT,
    keepalive=60
)
mqtt.set_callback(callback)
mqtt.connect()
mqtt.subscribe(TOPIC.encode())
print("Subscribed to", TOPIC)

try:
    while True:
        mqtt.wait_msg()
finally:
    try:
        mqtt.disconnect()
    except OSError:
        pass