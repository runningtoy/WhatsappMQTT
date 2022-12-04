# WhatsappMQTT

WhatsappMQTT is a python program running in docker that connects to a mqtt server and provides an interface to the WhatsApp messaging service.

## Installation
setup `yowsup`  profile

create `Dockerfile`

```
FROM python:3.6.8
#PACOTE REQUER PYTHON 3.6.X
#user/password
RUN mkdir /app
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser
USER root

ENV PYTHONDONTWRITEBYTECODE=1
#Instalando pacotes necessários
ENV PYTHONUNBUFFERED=1
RUN apt install -y git
WORKDIR /app
RUN git clone -b Desarrollo https://github.com/Rodrigosolari/yowsup.git .

#RUN sed -i 's/_MD5_CLASSES = "[^"]*"/_MD5_CLASSES = "Qc0kUxteJdDJSpeLPeHMKQ=="/g' /app/yowsup/env/env_android.py
#RUN sed -i 's/_VERSION = "[^"]*"/_VERSION = "2.22.23.84"/g' /app/yowsup/env/env_android.py

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN python -m pip install debugpy -t /tmp
RUN pwd
ENTRYPOINT ["/app/yowsup-cli"]
```

## how to get the MD5: [link->](https://iamjagjeetubhi.wordpress.com/2017/09/21/how-to-use-yowsup-the-python-whatsapp-library-in-ubuntu/)

download WhatsAPP APK from [here](https://www.whatsapp.com/android/)
```
wget https://github.com/mgp25/classesMD5-64/blob/master/dexMD5.py
pip install pyaxmlparser
python dexMD5.py WhatsApp.apk
```

create `docker-compose.yml`
```
version: '3.4'

services:
  yowsup:
    image: yowsup
    build:
      context: .
      dockerfile: ./Dockerfile
    ports:
      - 5678:5678
```

run (details see yowsup)
```
docker -D run -v /yowsup:/root/.config/yowsup/ yowsup registration --requestcode sms --config-phone YOURPHONENUMBER --config-cc 49 --config-mcc 262 --config-mnc 2
docker -D run -v /yowsup:/root/.config/yowsup/ yowsup registration --register XXXXXX --config-phone YOURPHONENUMBER --config-cc 49 --config-mcc 262 --config-mnc 2

```



clone this repo & edit `config.py` then run 
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
