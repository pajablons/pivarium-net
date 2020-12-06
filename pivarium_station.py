import configparser
import threading
import queue

import sensor_manager
import netio

class _Worker(threading.Thread):
    def __init__(self, mngr):
        super(_Worker, self).__init__(daemon = True)
        self._mngr = mngr
        self._task = None
        self._args = None
        self._activate = threading.Event()
        
    def grantTask(self, task, args = None):
        self._task = task
        self._args = args
        self._activate.set()

    def run(self):
        while self._activate.wait():
            self._task(self._args)
            self._activate.clear()
            self._mngr.avail_worker(self)


class RoutingManager:
    _WORKER_COUNT = 25

    def __init__(self, sensor_mngr):
        self._inQueue = queue.SimpleQueue()
        self._outQueue = queue.SimpleQueue()
        self.connections = {}
        self.sensor_mngr = sensor_mngr

        self._workerLock = threading.Lock()        
        self._workerpool = set()
        self._createWorkers(self._WORKER_COUNT)

    def startRouting(self):
        threading.Thread(daemon = True, target = self._readQueue).start()
        threading.Thread(daemon = True, target = self._writeQueue).start()

    def _readQueue(self):
        requestKeys = {
            "SENSE": self._task_sense
        }

        #TODO: isAlive
        while True:
            connID, data = self._inQueue.get()
            msgSplit = data.split(maxsplit = 1)
            reqKey = msgSplit[0]
            self._task_worker(requestKeys[reqKey], msgSplit[1])

    def _task_sense(self, sensor_id):
        self.sensor_mngr.read_sensor_by_id(sensor_id)

    def _writeQueue(self):
        #TODO: isAlive
        while True:
            connID, data = self._outQueue.get()
            self._send_msg(connID, data)

    def _createWorkers(self, count):
        with self._workerLock:
            for x in range(0, count):
                newWorker = _Worker(self)
                newWorker.start()
                self._workerpool.add(newWorker)

    def send(self, cid, msg):
        self._outQueue.put((cid, msg))

    def avail_worker(self, worker):
        with self._workerLock:
            self._workerpool.add(worker)

    def _task_worker(self, task, args = None):
        if len(self._workerpool) == 0:
            _createWorkers(self, _WORKER_COUNT)

        worker = None
        with self._workerLock:
            worker = self._workerpool.pop()
        worker.grantTask(task, args)

    def add_connection(self, connection):
        self.connections[connection.ident()] = connection
        self._task_worker(self._readConnStream, connection)

    def _send_msg(self, target, msg):
        self.connections[target].write(msg)
        
    def _readConnStream(self, connection):
        #TODO: isAlive
        while True:
            msg = connection.read()
            self._inQueue.put((connection.ident(), msg))

def read_sense_results(sensor_manager, route_manager, hub_id):
    #TODO: isAlive
    while True:
        sid, result = sensor_manager.requestNextResult()
        output = "SRES {} {}".format(sid, result)
        route_manager.send(hub_id, output)

def load_cfg(cfg_file_name):
    config_station = configparser.ConfigParser()
    config_station.read(cfg_file_name)

    sensor_config_file = config_station['Extensions']['Sensor_Config']
    config_sensors = configparser.ConfigParser()
    config_sensors.read(sensor_config_file)

    return config_station, config_sensors

def establishHubConnection(port):
    hubConn = netio.Connection(0)
    hubConn.receive_connection(port)
    return hubConn

config_station, config_sensors = load_cfg('settings_station.cfg')

sensor_manager = sensor_manager.SensorManager(config_sensors)
route_manager = RoutingManager(sensor_manager)

hubConn = establishHubConnection(int(config_station['NETWORK']['Bind_Port']))
route_manager.add_connection(hubConn)
route_manager.startRouting()

threading.Thread(daemon=True, target=read_sense_results, args=(sensor_manager, route_manager, hubConn.ident())).start()
