import logging
import os
import adafruit_dht
import board

from sensors.meta.data import Measurement
from sensors.meta.sensor import AbstractSensor

logger = logging.LoggerAdapter(logging.getLogger("sensiot"), {"class": os.path.basename(__file__)})

class DHT(AbstractSensor):

    def __init__(self, name, config, event, queue):
        super(DHT, self).__init__(name, config, event, queue)
        self.id = config['id']
        self.gpio = config['gpio']
        self.short_type = config['short_type']
        self.interval = config['interval']
        self.type = "DHT{}".format(self.short_type)#DHT22
        logger.info("{} initialized successfully".format(self.name))

    def read(self):
        self.event.wait(self.interval)
        logger.info("Reading data from GPIO...")
        #dht_device = adafruit_dht.self.type(board.self.gpio)
        #dht_device = adafruit_dht.DHT22(config['board_number'])
        dht_device = adafruit_dht.DHT22(board.D+self.gpio)
        #dht_device = adafruit_dht.DHT22(board.D25)
        measurement = Measurement(self.id, self.type)
        if dht_device :
            try:
                measurement.add("temperature", dht_device.temperature, "°C")
                measurement.add("humidity", dht_device.humidity, "%")
                logger.info("Data received: {}".format(measurement))
                return [measurement]
            except RuntimeError as error:
                # Errors happen fairly often, DHT's are hard to read, just keep going
                print(error.args[0])
            except Exception as error:
                    #dht_device.exit()
                    raise error

