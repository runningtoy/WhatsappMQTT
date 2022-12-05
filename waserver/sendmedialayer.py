from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers import YowLayerEvent, EventCallback
from yowsup.layers.network import YowNetworkLayer
import sys
from yowsup.common import YowConstants
import datetime
import time
import os
import logging
import threading
import base64
from yowsup.layers.protocol_groups.protocolentities      import *
from yowsup.layers.protocol_presence.protocolentities    import *
from yowsup.layers.protocol_messages.protocolentities    import *
from yowsup.layers.protocol_ib.protocolentities          import *
from yowsup.layers.protocol_iq.protocolentities          import *
from yowsup.layers.protocol_contacts.protocolentities    import *
from yowsup.layers.protocol_chatstate.protocolentities   import *
from yowsup.layers.protocol_privacy.protocolentities     import *
from yowsup.layers.protocol_media.protocolentities       import *
from yowsup.layers.protocol_media.mediauploader import MediaUploader
from yowsup.layers.protocol_profiles.protocolentities    import *
from yowsup.common.tools import Jid
from yowsup.common.optionalmodules import PILOptionalModule
from yowsup.layers.axolotl.protocolentities.iq_key_get import GetKeysIqProtocolEntity



logger = logging.getLogger(__name__)

class SendMedia(YowInterfaceLayer):

    PROP_MESSAGES = "org.openwhatsapp.yowsup.prop.sendclient.queue" #list of (jid, message) #tuples
    
    
    def __init__(self):
        super(SendMedia, self).__init__()
        self.ackQueue = []
        self.lock = threading.Condition()
        self.connected = True
        self.jidAliases = {
            # "NAME": "PHONE@s.whatsapp.net"
        }

    @ProtocolEntityCallback("success")
    def onSuccess(self, successProtocolEntity):
        self.connected = True
        self.lock.acquire()
        for target in self.getProp(self.__class__.PROP_MESSAGES, []):
            phone, filename, mediafiletype = target
            #print("\n %s" % phone)
            #print("\n %s" % filename)
            #print("\n %s" % mediafiletype)
            #self.audio_send(phone, message, mediafiletype)

            if mediafiletype == "image":
                self.image_send(phone, filename)
            elif mediafiletype == "audio":
                self.audio_send(phone, filename)
            elif mediafiletype == "video":
                self.video_send(phone, filename)
            else:
                print("Invalid file")
        self.lock.release()


    @ProtocolEntityCallback("ack")
    def onAck(self, entity):
        self.lock.acquire()
        if entity.getId() in self.ackQueue:
            self.ackQueue.pop(self.ackQueue.index(entity.getId()))

        if not len(self.ackQueue):
            self.lock.release()
            logger.info("Message sent")
            raise KeyboardInterrupt()

        self.lock.release()
        
    @ProtocolEntityCallback("iq")
    def onIq(self, entity):
        if not isinstance(entity, ResultStatusesIqProtocolEntity):  # already printed somewhere else
            print("ProtocolEntityCallback(\"iq\"): \n %s" % entity)
    
    @ProtocolEntityCallback("failure")
    def onFailure(self, entity):
        self.connected = False
        self.output("Login Failed, reason: %s" % entity.getReason(), prompt = False)
    
    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        self.toLower(entity.ack())    
    #--------------------------------------------------------------------------------------------------------------------------------
    #---------------------------------------------------image------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------------------

    def video_send(self, number, path, caption = None):
        self.media_send(number, path, RequestUploadIqProtocolEntity.MEDIA_TYPE_VIDEO)

    def image_send(self, number, path, caption = None):
        self.media_send(number, path, RequestUploadIqProtocolEntity.MEDIA_TYPE_IMAGE)

    def audio_send(self, number, path):
        self.media_send(number, path, RequestUploadIqProtocolEntity.MEDIA_TYPE_AUDIO)
      

    def media_send(self, number, path, mediaType, caption = None):
        #print("number %s;path %s; mediaType%" % (number, path,mediaType))        
        if self.assertConnected():
            jid = self.aliasToJid(number)
            print("Receiver JID %s" % (jid))    
            entity = RequestUploadIqProtocolEntity(mediaType, filePath=path)
            print("entity DONE %s" % (entity))    
            successFn = lambda successEntity, originalEntity: self.onRequestUploadResult(jid, mediaType, path, successEntity, originalEntity, caption)
            errorFn = lambda errorEntity, originalEntity: self.onRequestUploadError(jid, path, errorEntity, originalEntity)
            print("before _sendIq") 
            self._sendIq(entity, successFn, errorFn)
            print("after _sendIq")            
            
            
    def doSendMedia(self, mediaType, filePath, url, to, ip = None, caption = None):
        print("path %s; mediaType%; url %s;to %s" % (filePath,mediaType,url,to)) 
        if mediaType == RequestUploadIqProtocolEntity.MEDIA_TYPE_IMAGE:
        	entity = ImageDownloadableMediaMessageProtocolEntity.fromFilePath(filePath, url, ip, to, caption = caption)
        elif mediaType == RequestUploadIqProtocolEntity.MEDIA_TYPE_AUDIO:
        	entity = AudioDownloadableMediaMessageProtocolEntity.fromFilePath(filePath, url, ip, to)
        elif mediaType == RequestUploadIqProtocolEntity.MEDIA_TYPE_VIDEO:
        	entity = VideoDownloadableMediaMessageProtocolEntity.fromFilePath(filePath, url, ip, to, caption = caption)
        self.toLower(entity)


    ########### callbacks ############
    

    def onRequestUploadResult(self, jid, mediaType, filePath, resultRequestUploadIqProtocolEntity, requestUploadIqProtocolEntity, caption = None):
        print("onRequestUploadResult %s jid %s" % (filePath, jid))
        if resultRequestUploadIqProtocolEntity.isDuplicate():
            self.doSendMedia(mediaType, filePath, resultRequestUploadIqProtocolEntity.getUrl(), jid,
                             resultRequestUploadIqProtocolEntity.getIp(), caption)
        else:
            successFn = lambda filePath, jid, url: self.doSendMedia(mediaType, filePath, url, jid, resultRequestUploadIqProtocolEntity.getIp(), caption)
            mediaUploader = MediaUploader(jid, self.getOwnJid(), filePath,
                                      resultRequestUploadIqProtocolEntity.getUrl(),
                                      resultRequestUploadIqProtocolEntity.getResumeOffset(),
                                      successFn, self.onUploadError, self.onUploadProgress, asynchronous=False)
            mediaUploader.start()

    def onRequestUploadError(self, jid, path, errorRequestUploadIqProtocolEntity, requestUploadIqProtocolEntity):
        print("Request upload for file %s for %s failed" % (path, jid))

    def onUploadError(self, filePath, jid, url):
        print("Upload file %s to %s for %s failed!" % (filePath, url, jid))

    def onUploadProgress(self, filePath, jid, url, progress):
        print("%s => %s, %d%% \r" % (os.path.basename(filePath), jid, progress))
        #sys.stdout.flush()

    def assertConnected(self):
        if self.connected:
            print("connected")
            return True
        else:
            print("Not connected")
            return False
            
           

    @EventCallback(YowNetworkLayer.EVENT_STATE_DISCONNECTED)
    def onStateDisconnected(self,layerEvent):
        self.output("Disconnected: %s" % layerEvent.getArg("reason"))
        if self.disconnectAction == self.__class__.DISCONNECT_ACTION_PROMPT:
           self.connected = False
           self.notifyInputThread()
        else:
           os._exit(os.EX_OK)
            
    def aliasToJid(self, calias):
        for alias, ajid in self.jidAliases.items():
            if calias.lower() == alias.lower():
                return Jid.normalize(ajid)

        return Jid.normalize(calias)

    def jidToAlias(self, jid):
        for alias, ajid in self.jidAliases.items():
            if ajid == jid:
                return alias
        return jid


    ########### ib #######################
    def ib_clean(self, dirtyType):
        if self.assertConnected():
            entity = CleanIqProtocolEntity("groups", YowConstants.DOMAIN)
            self.toLower(entity)

    def ping(self):
        if self.assertConnected():
            entity = PingIqProtocolEntity(to = YowConstants.DOMAIN)
            self.toLower(entity)