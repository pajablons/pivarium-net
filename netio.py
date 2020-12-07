import socket
import threading
import queue

#TODO: message delimiters

DELIMITER = '\r'

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
        cache = ''
        #TODO: "is-alive"
        while True:
            msg = "{}{}".format(cache, self.readMsg())
            cache = ''
            msgSplit = msg.split('\r')
            for x in range(0, len(msgSplit) - 1):
                self._enqueue(msgSplit[x])
            if not msg.endswith('\r'):
                cache = msgSplit[len(msgSplit) - 1]

class _Writer(_ConnIO):
    def __init__(self, netsock, addr, manager, msgQ):
        super(_Writer, self).__init__(netsock, addr, manager, msgQ)

    def sendMsg(self, data):
        print("Writing: {}".format(data))
        self._enqueue("{}\r".format(data).encode('ascii'))

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

    def initiate_connection(self, address, port):
        self._remoteaddr = address
        self._port = port

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((address, port))

        self._conn = sock
        self._sockReader = _Reader(self._conn, self._remoteaddr, self, self._inQueue)
        self._sockWriter = _Writer(self._conn, self._remoteaddr, self, self._outQueue)

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
