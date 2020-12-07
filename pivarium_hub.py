import schedule
import configparser
import random
import time
import datetime
import threading
import sqlite3
import queue

import netio

class DBWriter:
    def __init__(self, dbf):
        self._dbf = dbf
        self._conn = sqlite3.connect(dbf)
        self._cursor = self._conn.cursor()
        self._actQueue = queue.SimpleQueue()
        threading.Thread(target = self._executeQueue, daemon = True).start()

    def _executeQueue(self):
        #TODO: isAlive
        conn = sqlite3.connect(self._dbf)
        cursor = conn.cursor()
        while True:
            task = self._actQueue.get()
            print(*task)
            cursor.execute(*task)
            conn.commit()

    def table_exists(self, tablename):
        self._cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tablename,))
        return not len(self._cursor.fetchall()) == 0

    def execute(self, cmd):
        self._actQueue.put(cmd)

    def insert(self, table, entry):
        query = ('INSERT INTO {} VALUES {}'.format(table, entry),)
        self._actQueue.put(query)

class Hub:
    def __init__(self):
        self.stations = {}
        self.dbwriter = DBWriter('pivarium.db')

    def addStation(self, station):
        self.stations[station.name] = station
        if not self.dbwriter.table_exists(station.name):
            self.dbwriter.execute(("CREATE TABLE {} (sensorname text, datetime text, reading_id INTEGER NOT NULL PRIMARY KEY, value text)".format(station.name),))

        threading.Thread(target = self._readConnection, args=(station,)).start()
        threading.Thread(target = self._writeConnection, args=(station,)).start()

    def _readConnection(self, station):
        conn = station.connection
        while True:
            msg = conn.read().split()
            if msg[1] == "SRES":
                tableText = "{}(sensorname, datetime, value)".format(station.name)
                sname = station.sensorsById[msg[2]]
                dt = datetime.datetime.now().__str__()
                value = msg[3]

                self.dbwriter.insert(tableText, '(\'{}\', \'{}\', \'{}\')'.format(sname, dt, value))

    def _writeConnection(self, station):
        conn = station.connection
        
        while True:
            req = station.reqQueue.get()
            conn.write(req)

class Sensor:
    def __init__(self, name, ident, stype):
        self.name = name
        self.ident = ident
        self.stype = stype

class Station:
    def __init__(self, address, port, ident):
        self.connection = None
        self.address = address
        self.port = port
        self.stID = ident
        self.sensors = {}
        self.sensorsById = {}
        self.name = None
        self.reqQueue = queue.SimpleQueue()

    def connect(self):
        self.connection = netio.Connection(self.stID)
        self.connection.initiate_connection(self.address, self.port)
        self.receiveStationData()

    def sense(self, sensor):
        self.reqQueue.put("SENSE {}".format(sensor))
    
    def receiveStationData(self):
        sdata = self.connection.read()
        lines = sdata.split('\n')

        self.name = lines[0].split(':')[1]
        for x in range(1, len(lines)):
            line = lines[x]
            sName = None
            sIdent = None
            sType = None
            subsplit = line.split('|')
            for pair in subsplit:
                key, value = pair.split(':')
                if key == 'sname':
                    sName = value
                elif key == 'stype':
                    sType = value
                elif key == 'sid':
                    sIdent = value

            self.sensors[sName] = Sensor(sName, sIdent, sType)
            self.sensorsById[sIdent] = sName

def load_cfg(cfg_file_name):
    config_hub = configparser.ConfigParser()
    config_hub.read(cfg_file_name)

    stationListFile = config_hub['STATIONS']['stationfile']
    stationList = configparser.ConfigParser()
    stationList.read(stationListFile)

    return config_hub, stationList

def getRandomSensor(sname, phub):
    sid = random.randint(1, 2)
    phub.stations[sname].sense(sid)

def readSensor(connection):
    print(connection.read())


hub = Hub()

config, stationList = load_cfg('settings_hub.cfg')


for section in stationList.sections():
    address = stationList[section]['address']
    port = int(stationList[section]['port'])
    ident = stationList[section]['ident']

    station = Station(address, port, ident)
    station.connect()
    hub.addStation(station)

schedule.every(3).seconds.do(getRandomSensor, sname = "Test_Station_1", phub = hub)
while True:
    schedule.run_pending()
    time.sleep(1)
