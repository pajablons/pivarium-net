import Adafruit_DHT

class Extension:
    def __init__(self, extension_id, text_id, prot, address):
        self.ext_id = extension_id
        self.name = text_id
        self.protocol = self.validate_protocol(prot)
        self.gpio_address = address

    def validate_protocol(self, prot):
        valid = {
            'DHT22': Adafruit_DHT.DHT22
        }
        if prot not in valid:
            raise ValueError("Illegal protocol id.  Connection protocol must be in: %r." % valid.keys())
        return valid.get(prot)

class Sensor(Extension):
    def __init__(self, extension_id, text_id, prot, address, s_type):
        super(Sensor, self).__init__(extension_id, text_id, prot, address)
        self.sensor_type, self.sensor_reader = self._validate_sensor_type(s_type)

    def _validate_sensor_type(self, s_type):
        valid = {
            "Humidity": self._read_humidity,
            "Temperature": self._read_temp
        }
        if s_type not in valid:
            raise ValueError("Illegal sensor type.  Sensor must be one of: %r." % valid.keys())
        return s_type, valid[s_type]

    def _read_humidity(self):
        humidity = Adafruit_DHT.read_retry(self.protocol, self.gpio_address)[0]

        if humidity is not None:
            return humidity
        else:
            return -1

    def _read_temp(self):
        temp = Adafruit_DHT.read_retry(self.protocol, self.gpio_address)[1]
        
        if temp is not None:
            return temp
        else:
            return -1

    def read_sensor(self):
        return self.sensor_reader()

class Switch(Extension):
    def __init__(self, extension_id, text_id, prot, s_type):
        raise Exception("Switches not yet implimented.")
