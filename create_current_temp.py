import paho.mqtt.client as mqtt
import json
from mqtt_helper import mqtt_helper
import statistics
from datetime import datetime

location = "temp_aggregator"

mqtt_helper = mqtt_helper(location)
server_address = "192.168.0.10"

topic_temp_lounge = "home/inside/sensor/lounge"
topic_temp_master = "home/inside/sensor/master"
topic_temp_joel = "home/inside/sensor/joel"
topic_temp_layla = "home/inside/sensor/layla"

topic_status_lounge = "status/sensor/lounge"
topic_status_master = "status/sensor/master"
topic_status_joel = "status/sensor/joel"
topic_status_layla = "status/sensor/layla"

output_topic = "home/inside/sensor/CurrentTemp"

lounge_temp = 21
master_temp = 21
joel_temp = 21
layla_temp = 21

lounge_status = "online"
master_status = "online"
joel_status = "online"
layla_status = "online"

temp_list = []

period_start = datetime.now()


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe([(topic_status_lounge,0),(topic_temp_lounge,0),(topic_status_master,0),(topic_temp_master,0),(topic_status_joel,0),(topic_temp_joel,0),(topic_status_layla,0),(topic_temp_layla,0)])

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global lounge_temp
    global lounge_status
    global master_temp
    global master_status
    global joel_temp
    global joel_status    
    global layla_temp
    global layla_status  
    global temp_list
    global period_start

    topic = msg.topic
    data = str(msg.payload.decode("utf-8"))
    jsonData=json.loads(data)    

    #print(jsonData)

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

    elif topic == topic_status_layla:
        layla_status = jsonData["status"]

    elif topic == topic_temp_layla:
        layla_temp = jsonData["temperature"]

    #print(lounge_status, lounge_temp, master_status, master_temp, joel_status, joel_temp)

    if lounge_status == "online":
        temp = lounge_temp
    
    elif master_status == "online":
        temp = master_temp

    elif layla_status == "online":
        temp = layla_temp

    else:
        temp = joel_temp

    temp_list.append(temp)

    temp_list = temp_list[-3:]

    currentTemp = round(statistics.mean(temp_list),1)

    msg = {"CurrentTemp":currentTemp}

    if (datetime.now() - period_start).total_seconds() > 5:
        
        mqtt_helper.publish_generic_message(output_topic, msg)

        period_start = datetime.now()

        mqtt_helper.publish_status()


client1 = mqtt.Client()
client1.on_connect = on_connect
client1.on_message = on_message

client1.connect(server_address)

client1.loop_forever()


