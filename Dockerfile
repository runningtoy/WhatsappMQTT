FROM python:3.6
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

RUN mkdir -p /usr/src/app/waserver
WORKDIR /usr/src/app/waserver

RUN git clone -b Desarrollo https://github.com/Rodrigosolari/yowsup.git .

#uncomment and change following lines if needed
#RUN sed -i 's/_MD5_CLASSES = "[^"]*"/_MD5_CLASSES = "YlajJPPGUUP1Ptcic2XKNA=="/g'  /usr/src/app/waserver/yowsup/env/env_android.py
#RUN sed -i 's/_VERSION = "[^"]*"/_VERSION = "2.18.105"/g'  /usr/src/app/waserver/yowsup/env/env_android.py

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
#RUN python setup.py install
WORKDIR /usr/src/app
RUN python -m pip install debugpy -t /tmp
RUN CFLAGS="$CFLAGS -L/lib" pip install pillow
RUN python -m pip install paho-mqtt

COPY . /usr/src/app

RUN rm /usr/src/app/waserver/config.py
COPY ./waserver/config.py /usr/src/app/waserver/config.py

# python waserver/waserver.py noconn

CMD ["python", "waserver/waserver.py"]

#ENTRYPOINT ["/app/yowsup-cli"]






#FROM frolvlad/alpine-python2

#RUN apk update
#RUN apk add ca-certificates gcc musl-dev libjpeg-turbo-dev zlib-dev bash zlib python-dev readline-dev ncurses-dev make

#RUN CFLAGS="$CFLAGS -L/lib" pip install pillow
#RUN pip install yowsup2
#RUN pip install paho-mqtt

#RUN mkdir -p /usr/src/app
#WORKDIR /usr/src/app

#COPY . /usr/src/app

#RUN rm /usr/src/app/waserver/config.py
#COPY ./waserver/config-prod.py /usr/src/app/waserver/config.py

#RUN python waserver/waserver.py noconn

#CMD ["python", "waserver/waserver.py"]
