import Adafruit_DHT
import sensor
import threading

class Extension(threading.Thread):
    def __init__(self, extension_id, text_id, prot, address):
        super(Extension, self).__init__()
        self.ext_id = extension_id
        self.name = text_id
        self.gpio_address = address
        self.protocol = self.validate_protocol(prot)
        self.instance = self.generate_instance(self.protocol)

    def generate_instance(self, prot):
        if prot is Adafruit_DHT.DHT22:
            return None
        elif prot is sensor.SHT20:
            return sensor.SHT20(1, int(self.gpio_address, 16))
        elif prot is sensor.DS18B20:
            return sensor.DS18B20(self.gpio_address)
        else:
            return None

    def validate_protocol(self, prot):
        valid = {
            'DHT22': Adafruit_DHT.DHT22,
            'SHT20': sensor.SHT20,
            'DS18B20': sensor.DS18B20
        }
        if prot not in valid:
            raise ValueError("Illegal protocol id.  Connection protocol must be in: %r." % valid.keys())
        return valid.get(prot)

class Sensor(Extension):
    def __init__(self, extension_id, text_id, prot, address, s_type, killEvent, rEvent, manager):
        super(Sensor, self).__init__(extension_id, text_id, prot, address)
        self.manager = manager
        self.sensor_type, self.sensor_reader = self._validate_sensor_type(s_type)
        self.readEvent = rEvent
        self.shutdownEvent = killEvent

    def _validate_sensor_type(self, s_type):
        valid = {
            "Humidity": self._sense_select_humidity,
            "Temperature": self._sense_select_temp
        }
        if s_type not in valid:
            raise ValueError("Illegal sensor type.  Sensor must be one of: %r." % valid.keys())
        return s_type, valid[s_type]()

    def run(self):
        while not self.shutdownEvent.isSet():
            if self.readEvent.wait(5):
                result = self.read_sensor()
                self.manager.registerReadResult((self.ext_id, result))
                self.readEvent.clear()

    def _sense_select_humidity(self):
        processors = {
            sensor.SHT20: lambda: self.instance.humidity(),
            Adafruit_DHT.DHT22: lambda: Adafruit_DHT.read_retry(self.protocol, self.gpio_address)[0]
        }

        return processors[self.protocol]

    def _sense_select_temp(self):
        processors = {
            sensor.SHT20: lambda: self.instance.temperature().C,
            sensor.DS18B20: lambda: self.instance.temperature().C,
            Adafruit_DHT.DHT22: lambda: Adafruit_DHT.read_retry(self.protocol, self.gpio_address)[1]
        }
        
        return processors[self.protocol]

    def read_sensor(self):
        return self.sensor_reader()

class Switch(Extension):
    def __init__(self, extension_id, text_id, prot, s_type):
        raise Exception("Switches not yet implimented.")
