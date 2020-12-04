import configparser
import threading

import sensor_manager

def load_cfg(cfg_file_name):
    config_station = configparser.ConfigParser()
    config_station.read(cfg_file_name)

    sensor_config_file = config_station['Extensions']['Sensor_Config']
    config_sensors = configparser.ConfigParser()
    config_sensors.read(sensor_config_file)

    return config_station, config_sensors

config_station, config_sensors = load_cfg('settings_station.cfg')

sensor_manager = sensor_manager.SensorManager(config_sensors)
for sensor_name in sensor_manager.get_sensor_names():
    sensor_manager.read_sensor_by_name(sensor_name)

for x in range(2):
    print(sensor_manager.requestNextResult())

sensor_manager.shutdown_sensors()
