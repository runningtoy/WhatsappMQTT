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
from axolotl.kdf.hkdfv3 import HKDFv3
from axolotl.util.byteutil import ByteUtil
import binascii
import hashlib


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

def pad(s):
        return s + ((16-len(s) % 16) * bytes('{','ascii'))

def encryptImg(img, refkey):
    img = pad(img)
    derivative = HKDFv3().deriveSecrets(binascii.unhexlify(refkey), binascii.unhexlify("576861747341707020496d616765204b657973"), 112)
    parts = ByteUtil.split(derivative, 16, 32)
    iv = parts[0]
    cipherKey = parts[1]
    cipher = AES.new(key=cipherKey, mode=AES.MODE_CBC, IV=iv)
    imgEnc=cipher.encrypt(img)
    return imgEnc[:-6]


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
        
        sourcePath="/usr/src/app/openhab-logo.png"
        
        filename = os.path.basename(sourcePath)
        #filetype = MimeTools.getMIME(filename)
        f = open(sourcePath, 'rb')
        stream = f.read()
        f.close()
        refkey = binascii.hexlify(os.urandom(112))
        stream=encryptImg(stream,refkey)
        
        base=os.path.basename(filename)
        #filename=os.path.dirname(sourcePath)+"/"+os.path.splitext(base)[0]+"enc"+os.path.splitext(base)[1]
        filename=os.path.dirname(sourcePath)+"/"+os.path.splitext(base)[0]+".enc"

        fenc = open(filename, 'wb')  
        fenc.write(stream)
        fenc.seek(0, 2)
        filesize=fenc.tell()
        fenc.close()

        sha1 = hashlib.sha256()
        sha1.update(stream)
        b64Hash = base64.b64encode(sha1.digest())
        
        
        
        
        #stack = sendmediafile(profile, [([payload["phone"], payload["image"], image])])
        print("File exitst?: %s" % filename)
        print(os.path.exists(filename))
        stack = YowsupSendStack(profile, [("491776111183", filename, "image")],"image")
        
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

