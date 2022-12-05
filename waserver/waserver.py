import sys
from stack import YowsupSendStack
#from sendmediastack import sendmediafile
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
from Crypto.Cipher import AES
import hashlib


def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))

def enc_image(input_data,key,iv,filepath,filename):
    cfb_cipher = AES.new(key, AES.MODE_CFB, iv)
    enc_data = cfb_cipher.encrypt(input_data)
    
    base=os.path.basename(filename)
    filename=filepath+"/"+os.path.splitext(base)[0]+".enc"
    #filename=filepath+"/"+os.path.splitext(base)[0]+"enc"+os.path.splitext(base)[1]
    enc_file = open(filename, "wb")
    enc_file.write(enc_data)
    enc_file.close()
    return filename

def on_message(mqttc, obj, msg):
    if msg.topic == "whatsapp/textmessage":
        m_decode=str(msg.payload.decode("utf-8","ignore"))
        payload = json.loads(m_decode)
        print(json.dumps(payload, sort_keys=True, indent=4))
        config_manager = ConfigManager()
        profile = YowProfile(config.PHONE)
        stack = YowsupSendStack(profile, [([payload["phone"], payload["message"]])],"txt")
        stack.start()
    if msg.topic == "whatsapp/image":
        m_decode=str(msg.payload.decode("utf-8","ignore"))
        payload = json.loads(m_decode)
        print(json.dumps(payload, sort_keys=True, indent=4))
        config_manager = ConfigManager()
        profile = YowProfile(config.PHONE)
        
        filename="/usr/src/app/openhab-logo.png"
        file_path_e = os.path.dirname(filename)

        #GENERATE KEY & INITIALIZATION VECTOR
        hash_string = 'confidential data'
        hash=hashlib.sha256(hash_string.encode())
        p = hash.digest()
        key = p
        iv = p.ljust(16)[:16]
        print("Encoding key is: ",key)

        input_file = open(filename,'rb')
        input_data = input_file.read()
        input_file.close()
        filename=enc_image(input_data,key,iv,file_path_e,filename)
        
        
        
        
        #stack = sendmediafile(profile, [([payload["phone"], payload["image"], image])])
        print("File exitst?: %s" % filename)
        print(os.path.exists(filename))
        stack = YowsupSendStack(profile, [("491xxxxxxxxxx", filename, "image")],"image")
        
        #stack = sendmedia.sendmediafile(credentials, [([self.args["media"][0], self.args["media"][1], self.args["media"][2]])])
        #arg[1] = phone number.
        #arg[2] = path of media, it may be image, audio or video.
        #arg[3] = static text 'image'/ 'audio'/ 'video', this is based on your media selected
        
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
mqttc.subscribe("whatsapp/image")

mqttc.loop_forever()

