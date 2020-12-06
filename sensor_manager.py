import Adafruit_DHT
import configparser
import threading
import queue

import extensions

class SensorManager:
    def __init__(self, config_sensors):
        self.shutdownEvent = threading.Event()
        self.senseResultQueue = queue.SimpleQueue()
        self.sensor_dict, self.reader_event_dict = self._load_sensors(config_sensors)
    
    def _load_sensors(self, config_sensors):
        sensor_dict = {}
        reader_event_dict = {}
        for section in config_sensors.sections():
            ext_id = config_sensors[section]["Sensor_ID"]
            reader_event_dict[ext_id] = threading.Event()
            sensor = extensions.Sensor(
                extension_id = ext_id,
                text_id = config_sensors[section]["Name"], 
                prot = config_sensors[section]["Connection"], 
                address = config_sensors[section]["GPIO_Address"], 
                s_type = config_sensors[section]["Type"],
                killEvent = self.shutdownEvent,
                rEvent = reader_event_dict[ext_id],
                manager = self
            )
            sensor_dict[ext_id] = sensor
            sensor.start()
        return sensor_dict, reader_event_dict

    def _poll_sensor(self, sensor):
        self.reader_event_dict[sensor.ext_id].set()
#        value = sensor.read_sensor()
#        return '{}: {}'.format(sensor.name, value)

    def registerReadResult(self, sensorResult):
        self.senseResultQueue.put(sensorResult)

    def requestNextResult(self):
        return self.senseResultQueue.get()

    def shutdown_sensors(self):
        self.shutdownEvent.set()

    def read_sensor_by_id(self, ident):
        self._poll_sensor(self.sensor_dict[ident])

    def get_sensor_names(self):
        return self.sensor_dict.keys()
