import Adafruit_DHT
import configparser

import extensions

SENSORTYPE_HUMIDITY_TEMP = Adafruit_DHT.DHT22
PIN_HUMIDITY_TEMP = 4

def load_cfg(cfg_file_name):
    config_station = configparser.ConfigParser()
    config_station.read(cfg_file_name)

    sensor_config_file = config_station['Extensions']['Sensor_Config']
    config_sensors = configparser.ConfigParser()
    config_sensors.read(sensor_config_file)

    return config_station, config_sensors

def load_sensors(config_sensors):
    sensor_dict = {}
    for section in config_sensors.sections():
        sensor_name = config_sensors[section]["Name"]
        sensor = extensions.Sensor(
            extension_id = config_sensors[section]["Sensor_ID"], 
            text_id = sensor_name, 
            prot = config_sensors[section]["Connection"], 
            address = config_sensors[section]["GPIO_Address"], 
            s_type = config_sensors[section]["Type"]
        )
        sensor_dict[sensor_name] = sensor
    return sensor_dict

def poll_sensor(sensor):
    value = sensor.read_sensor()
    print('{}: {}'.format(sensor.name, value))

config_station, config_sensors = load_cfg('settings_station.cfg')
sensors = load_sensors(config_sensors)
for sensor_name in sensors:
    poll_sensor(sensors[sensor_name])
