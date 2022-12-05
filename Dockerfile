FROM python:3.6
#PACOTE REQUER PYTHON 3.6.X
#user/password
RUN mkdir /app
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser
USER root

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt install -y git

RUN mkdir -p /usr/src/app/waserver
WORKDIR /usr/src/app


RUN python -m pip install --upgrade pip
RUN python -m pip install debugpy -t /tmp
RUN CFLAGS="$CFLAGS -L/lib" pip install pillow
RUN python -m pip install paho-mqtt
RUN python -m pip install pycrypto

COPY . /usr/src/app

RUN rm /usr/src/app/waserver/config.py
COPY ./waserver/config.py /usr/src/app/waserver/config.py

#RUN sed -i 's/_MD5_CLASSES = "[^"]*"/_MD5_CLASSES = "Qc0kUxteJdDJSpeLPeHMKQ=="/g' /usr/src/app/waserver/yowsup/env/env_android.py
#RUN sed -i 's/_VERSION = "[^"]*"/_VERSION = "2.22.23.84"/g' /usr/src/app/waserver/yowsup/env/env_android.py

WORKDIR /usr/src/app/waserver
RUN python -m pip install -r requirements.txt
WORKDIR /usr/src/app

RUN chmod 777 /usr/src/app/openhab-logo.png
CMD ["python", "waserver/waserver.py"]

#ENTRYPOINT ["/app/yowsup-cli"]