import Adafruit_DHT
import configparser
import threading

import extensions

class SensorManager:
    def __init__(self, config_sensors):
        self.shutdownEvent = threading.Event()
        self.sensor_dict, self.reader_event_dict = self._load_sensors(config_sensors)
    
    def _load_sensors(self, config_sensors):
        sensor_dict = {}
        reader_event_dict = {}
        for section in config_sensors.sections():
            sensor_name = config_sensors[section]["Name"]
            reader_event_dict[sensor_name] = threading.Event()
            sensor = extensions.Sensor(
                extension_id = config_sensors[section]["Sensor_ID"], 
                text_id = sensor_name, 
                prot = config_sensors[section]["Connection"], 
                address = config_sensors[section]["GPIO_Address"], 
                s_type = config_sensors[section]["Type"],
                killEvent = self.shutdownEvent,
                rEvent = reader_event_dict[sensor_name]
            )
            sensor_dict[sensor_name] = sensor
            sensor.start()
        return sensor_dict, reader_event_dict

    def _poll_sensor(self, sensor):
        self.reader_event_dict[sensor.name].set()
#        value = sensor.read_sensor()
#        return '{}: {}'.format(sensor.name, value)

    def shutdown_sensors(self):
        self.shutdownEvent.set()

    def read_sensor_by_name(self, name):
        return self._poll_sensor(self.sensor_dict[name])

    def get_sensor_names(self):
        return self.sensor_dict.keys()
