ARG IMAGE_TARGET=alpine

# first image to download qemu and make it executable
FROM alpine AS qemu
ARG QEMU=x86_64
ARG QEMU_VERSION=v2.11.0
ADD https://github.com/multiarch/qemu-user-static/releases/download/${QEMU_VERSION}/qemu-${QEMU}-static /qemu-${QEMU}-static
RUN chmod +x /qemu-${QEMU}-static

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN apk --no-cache add git build-base libgpiod python3 python3-dev py3-pip && \
    pip3 install RPi.GPIO adafruit-circuitpython-dht && \
    pip3 install smbus2 adafruit-circuitpython-pcf8591


RUN apk add -U --no-cache py3-gevent py3-flask file && \
    pip3 install --no-cache-dir -r requirements.txt 

COPY src /app/
RUN chmod +x /app/manager.py

ENTRYPOINT ["/app/manager.py"]