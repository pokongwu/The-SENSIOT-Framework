import json
import logging
import os

from multiprocessing import Queue
from sensors.rain.pcf8591_lm393 import Rain
from utilities.nsq.nsq_reader import NsqReader


logger = logging.LoggerAdapter(logging.getLogger("sensiot"), {"class": os.path.basename(__file__)})

class Services:
    def __init__(self, config, event):
        self.config = config
        self.event = event
        self.services = {
            "local_manager": self.__create_local_manager,
            "prometheus_writer": self.__create_prometheus,
            "temperature_humidity_rain_sound_sensor": self.__create_temperature_humidity_rain_sound_sensor
        }

    def get_services(self, type):
        return self.services.get(type)()

    """
    Local Manager

    """
    def __get_local_configuration(self):
        local_configuration_path = self.config['services']['local_manager']['local_configuration']
        logger.info("Local configuration file set to {}".format(local_configuration_path))
        if os.path.isfile(local_configuration_path):
            with open(local_configuration_path, 'r') as file:
                configuration = json.load(file)
                return configuration
        else:
            logger.error("Local configuration file not found: {}".format(local_configuration_path))

    def __create_local_manager(self):
            from utilities.socket.socket_reader import SocketReader
            from utilities.local.metadata_appender import MetaDataAppender
            from utilities.local.local_manager import LocalManager
            from utilities.nsq.nsq_writer import NsqWriter

            threads = []
            local_configuration = self.__get_local_configuration()

            message_queue = Queue(maxsize=10)
            meta_queue = Queue(maxsize=10)

            socket_reader = SocketReader("SocketReader", self.event, message_queue)
            meta_data_appender = MetaDataAppender("MetaData", self.event, message_queue, meta_queue, local_configuration)
            nsq_writer = NsqWriter("NsqWriter", self.event, meta_queue, self.config['services']['nsq'])
            local_manager = LocalManager("LocalManager", self.event, {"local_manager": self.config['services']['local_manager'], "local_configuration": local_configuration, "utilities": self.config["utilities"]["logging"]})

            threads.append(socket_reader)
            threads.append(meta_data_appender)
            threads.append(nsq_writer)
            threads.append(local_manager)

            return threads

    """
    Temperature & Humidity , Rain and Sound Sensors

    """
    def __create_temperature_humidity_rain_sound_sensor(self):
            from utilities.socket.socket_writer import SocketWriter
            threads = []
            type = os.environ['TYPE']

            sensor_queue = Queue(maxsize=10)

            if type == "dht":
                from sensors.temperature_humidity.dht import DHT
                dht = DHT("DHT", self.config['configuration'], self.event, sensor_queue)
                threads.append(dht)
            elif type == "sound":
                from sensors.sound.pcf8591_lm358 import Sound
                sound = Sound("Sound", self.config['configuration'], self.event, sensor_queue)
                threads.append(sound)
            elif type == "rain":
                from sensors.rain.pcf8591_lm393 import Rain
                rain = Rain("Rain", self.config['configuration'], self.event, sensor_queue)
                threads.append(rain)
            elif type == "mock":
                from sensors.temperature_humidity.sensor_mock import SensorMock
                mock = SensorMock("Mock", self.event, sensor_queue, self.config['configuration'])
                threads.append(mock)
            else:
                logger.error("No sensortype selected: {}".format(type))

            socket_writer = SocketWriter("SocketWriter", self.event, sensor_queue, os.environ['SOCKET'])
            threads.append(socket_writer)

            return threads

    """
    Prometheus Writer

    """
    def __create_prometheus(self):
            from databases.prometheus.prometheus_writer import PrometheusWriter
            threads = []

            prometheus_queue = Queue(maxsize=10)

            nsq_reader = NsqReader("Prometheus_NsqReader", self.event, prometheus_queue, self.config['services']['nsq'], channel="prometheus_writer")
            prometheus_writer = PrometheusWriter("Prometheus_Writer", self.event, prometheus_queue, self.config['services']['prometheus_writer'])

            threads.append(nsq_reader)
            threads.append(prometheus_writer)

            return threads

