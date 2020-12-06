import socket
import threading

class _ConnIO(threading.Thread):
    def __init__(self, netsock, addr, manager, msgQ):
        self.iosock = netsock
        self.address = addr
        self.manager = manager
        self.msgQueue = msgQ

    def _enqueue(self, msg):
        msgQueue.put(msg)
    
    def pop():
        return self.msgQueue.get()

    def sendMsg(self, data):
        self.iosock.send(data.encode('ascii'))

class _Reader(_ConnIO):
    def __init__(self, netsock, addr, manager, msgQ):
        super(_ConnIO, self).__init__(netsock, addr, manager, msgQ)

    def readMsg(self, length=1024):
        return self.iosock.recv(length).decode('ascii')

    def run(self):
        #TODO: "is-alive"
        while True:
            self._enqueue(self.readMsg())

class _Writer(_ConnIO):
    def __init__(self, netsock, addr, manager, msgQ):
        super(_ConnIO, self).__init__(netsock, addr, manager, msgQ)

    def sendMsg(self, data):
        self.iosock.sendall(data.encode('ascii'))

    def run(self):
        #TODO: "is-alive"
        while True:
            self.sendMsg(self.pop())

def Connection:
    def __init__(self):
        self.conn = None
        self.remoteaddr = None
        
        self.sockReader = None
        self.sockWriter = None

        self.inQueue = SimpleQueue()
        self.outQueue = SimpleQueue()
       #This seems really stupid, I feel like the processing should happen in this same thread (asking the sensormanager to issue requests and requesting back the results), but then we lose encapsulation and 

       #New idea: Every time a received message is popped off the queue, dynamically create a new thread to handle that message, and only that message.  
       #That thread interprets the message, and requests a sense or switch.  It does NOT wait for the results of said switch or sense-- A single thread can handle ALL sending.... likely the Main thread

    def initiate_connection(self, address, port):
        self.remoteaddr = address
        self.port = port

        sock = socket.socket(AF_INET, socket.SOCK_STREAM)
        sock.connect((address, port))

        self.conn = sock
        self.sockReader = _Reader(self.conn, self.remoteaddr, self, self.inQueue)
        self.sockWriter = _Writer(self.conn, self.remoteaddr, self, self.outQueue)

        self.sockReader.start()
        self.sockWriter.start()
        
    def receive(self, port):
        self.port = port

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', port))
        sock.listen()
        self.conn, self.remoteaddr = sock.accept()
        sock.close()
        
        self.sockReader = _Reader(self.conn, self.remoteaddr, self, self.inQueue)
        self.sockWriter = _Writer(self.conn, self.remoteaddr, self, self.outQueue)

        self.sockReader.start()
        self.sockWriter.start()
