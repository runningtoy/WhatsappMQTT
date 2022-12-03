# WhatsappMQTT

Axiom is a python program that connects to a mqtt server and provides an interface to the WhatsApp messaging service.

## Installation

edit `config.py` & run 
```
docker-compose build
docker-compose up -d
```

## MQTT interface

### Sending messages
To send messages, publish to `whatsapp/textmessage`:

```json
{
  "phone": "4915112345678",
  "message": "Hello from a bot!"
}
```
