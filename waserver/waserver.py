import sys
from stack import YowsupSendStack
from yowsup.env import YowsupEnv
from yowsup.config.manager import ConfigManager
from yowsup.profile.profile import YowProfile

from yowsup.config.v1.config import Config
from yowsup import logger as yowlogger, formatter
from yowsup.layers.network.layer import YowNetworkLayer
from yowsup.layers.protocol_media.mediacipher import MediaCipher
from yowsup.common.tools import StorageTools

from consonance.structs.publickey import PublicKey
from consonance.structs.keypair import KeyPair
import sys, argparse, yowsup, logging, os
import base64
from google import protobuf
import consonance, dissononce, cryptography, axolotl

import paho.mqtt.client as mqtt
import json
import config



# CREDENTIALS = ("49722360368", "bO6GnxXW8iPSGYoFGhjLVQE0dFE=")
# CREDENTIALS = ("4915204295777", "IcQWRVBd7l9s7F8ZG+qBkkb1/CU=")
#def main():
    
#    config_manager = ConfigManager()
#    profile = YowProfile("4915223442934")

 #   stack = YowsupSendStack(profile, [(['491776111183', 'message_text'])],)
 #   stack.start()
    #if 'noconn' in sys.argv:
 #   sys.exit(0)

def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))


def on_message(mqttc, obj, msg):
    if msg.topic == "whatsapp/textmessage":
        m_decode=str(msg.payload.decode("utf-8","ignore"))
        payload = json.loads(m_decode)
        print(json.dumps(payload, sort_keys=True, indent=4))
        config_manager = ConfigManager()
        profile = YowProfile(config.PHONE)
        stack = YowsupSendStack(profile, [([payload["phone"], payload["message"]])],)
        stack.start()


def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)


mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
# Uncomment to enable debug messages
# mqttc.on_log = on_log
mqttc.connect(config.MQTT_HOST, config.MQTT_PORT, 60)
mqttc.subscribe("whatsapp/textmessage")

mqttc.loop_forever()

