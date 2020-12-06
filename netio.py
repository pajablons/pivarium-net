import socket
import threading
import queue

#TODO: message delimiters

class _ConnIO(threading.Thread):
    def __init__(self, netsock, addr, manager, msgQ):
        super(_ConnIO, self).__init__()
        self.iosock = netsock
        self.address = addr
        self.manager = manager
        self.msgQueue = msgQ

    def _enqueue(self, msg):
        self.msgQueue.put(msg)
    
    def pop(self):
        return self.msgQueue.get()

    def sendMsg(self, data):
        self.iosock.send(data.encode('ascii'))

class _Reader(_ConnIO):
    def __init__(self, netsock, addr, manager, msgQ):
        super(_Reader, self).__init__(netsock, addr, manager, msgQ)

    def readMsg(self, length=1024):
        return self.iosock.recv(length).decode('ascii')

    def run(self):
        #TODO: "is-alive"
        while True:
            msg = self.readMsg()
            self._enqueue(msg)

class _Writer(_ConnIO):
    def __init__(self, netsock, addr, manager, msgQ):
        super(_Writer, self).__init__(netsock, addr, manager, msgQ)

    def sendMsg(self, data):
        self._enqueue(data.encode('ascii'))

    def run(self):
        #TODO: "is-alive"
        while True:
            self.iosock.sendall(self.pop())

class Connection:
    def __init__(self, connID):
        self._connID = connID
        self._conn = None
        self._remoteaddr = None
        
        self._sockReader = None
        self._sockWriter = None

        self._inQueue = queue.SimpleQueue()
        self._outQueue = queue.SimpleQueue()
       #This seems really stupid, I feel like the processing should happen in this same thread (asking the sensormanager to issue requests and requesting back the results), but then we lose encapsulation and 

       #New idea: Every time a received message is popped off the queue, dynamically create a new thread to handle that message, and only that message.  
       #That thread interprets the message, and requests a sense or switch.  It does NOT wait for the results of said switch or sense-- A single thread can handle ALL sending.... likely the Main thread

    def initiate_connection(self, address, port):
        self._remoteaddr = address
        self._port = port

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((address, port))

        self._conn = sock
        self._sockReader = _Reader(self.conn, self.remoteaddr, self, self._inQueue)
        self._sockWriter = _Writer(self.conn, self.remoteaddr, self, self._outQueue)

        self._sockReader.start()
        self._sockWriter.start()
        
    def receive_connection(self, port):
        self._port = port

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', port))
        sock.listen()
        self._conn, self._remoteaddr = sock.accept()
        sock.close()
        
        self._sockReader = _Reader(self._conn, self._remoteaddr, self, self._inQueue)
        self._sockWriter = _Writer(self._conn, self._remoteaddr, self, self._outQueue)

        self._sockReader.start()
        self._sockWriter.start()

    def read(self):
        return self._sockReader.pop()

    def write(self, data):
        self._sockWriter.sendMsg(data)

    def ident(self):
        return self._connID
