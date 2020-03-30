import paho.mqtt.client as mqtt
import json
from mqtt_helper import mqtt_helper
import argparse
import logging

location = "temp_aggregator"

mqtt_helper = mqtt_helper(location)
server_address = "192.168.0.10"

topic_temp_lounge = "home/inside/sensor/lounge"
topic_temp_master = "home/inside/sensor/master"
topic_temp_joel = "home/inside/sensor/joel"

topic_status_lounge = "status/sensor/lounge"
topic_status_master = "status/sensor/master"
topic_status_joel = "status/sensor/joel"

output_topic = "home/inside/sensor/CurrentTemp"

lounge_temp = 21
master_temp = 21
joel_temp = 21

lounge_status = "online"
master_status = "online"
joel_status = "online"


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe([(topic_status_lounge,0),(topic_temp_lounge,0),(topic_status_master,0),(topic_temp_master,0),(topic_status_joel,0),(topic_temp_joel,0)])

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global lounge_temp
    global lounge_status
    global master_temp
    global master_status
    global joel_temp
    global joel_status    


    topic = msg.topic
    data = str(msg.payload.decode("utf-8"))
    jsonData=json.loads(data)    

    if topic == topic_status_lounge:
        lounge_status = jsonData["status"]

    elif topic == topic_temp_lounge:
        lounge_temp = jsonData["temperature"]

    elif topic == topic_status_master:
        master_status = jsonData["status"]

    elif topic == topic_temp_master:
        master_temp = jsonData["temperature"]

    elif topic == topic_status_joel:
        joel_status = jsonData["status"]

    elif topic == topic_temp_joel:
        joel_temp = jsonData["temperature"]

    if lounge_status == "online":
        currentTemp = lounge_temp
    
    elif master_status == "online":
        currentTemp = lounge_temp

    else:
        currentTemp = joel_temp

    dict_msg = {"CurrentTemp":currentTemp}
    msg = json.dumps(dict_msg)

    mqtt_helper.publish_generic_message(output_topic, msg)
    
    mqtt_helper.publish_status()


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(server_address)


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
client.enable_logger(logger)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_start()


