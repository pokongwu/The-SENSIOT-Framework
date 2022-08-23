import logging
import os
import time
import board

from adafruit_pcf8591.pcf8591 import PCF8591

from sensors.meta.data import Measurement
from sensors.meta.sensor import AbstractSensor

logger = logging.LoggerAdapter(logging.getLogger("sensiot"), {"class": os.path.basename(__file__)})

class Rain(AbstractSensor):

    def __init__(self, name, config, event, queue):
        super(Rain, self).__init__(name, config, event, queue)
        self.id = config['id']
        self.channel = config['channel']
        self.short_type = config['short_type']
        self.interval = config['interval']
        self.type = "LM{}".format(self.short_type)#LM393
        logger.info("{} initialized successfully".format(self.name))

    def read(self):
        self.event.wait(self.interval)
        logger.info("Reading data from Rain sensor...")
        i2c = board.I2C()
        pcf = PCF8591(i2c)
        read_raw = pcf.read(self.channel)
        read_value = read_raw * pcf.reference_voltage
        if read_value:
            measurement = Measurement(self.id, self.type)
            measurement.add("rain", read_value, "cm")
            logger.info("Data received: {}".format(measurement))
        return [measurement]