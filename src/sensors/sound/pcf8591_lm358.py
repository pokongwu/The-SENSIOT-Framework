import logging
import os
import time
import board

from adafruit_pcf8591.pcf8591 import PCF8591

from sensors.meta.data import Measurement
from sensors.meta.sensor import AbstractSensor

logger = logging.LoggerAdapter(logging.getLogger("sensiot"), {"class": os.path.basename(__file__)})

class Sound(AbstractSensor):

    def __init__(self, name, config, event, queue):
        super(Sound, self).__init__(name, config, event, queue)
        self.id = config['id']
        self.channel = config['channel']
        self.short_type = config['short_type']
        self.interval = config['interval']
        self.type = "PCF{}".format(self.short_type)#PCF8591
        logger.info("{} initialized successfully".format(self.name))

    def read(self):
        self.event.wait(self.interval)
        logger.info("Reading data from Sound sensor...")
        i2c = board.I2C()
        pcf = PCF8591(i2c)
        read_value = pcf.read(self.channel)
        if read_value:
            measurement = Measurement(self.id, self.type)
            measurement.add("sound", read_value, "dB")
            logger.info("Data received: {}".format(measurement))
        return [measurement]