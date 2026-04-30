from contextvars import ContextVar
from threading import Thread, Lock
from queue import Queue
import socket

_events = Queue() # List of events that have occurred in the network
_events_lock = Lock() # Lock for accessing the _events queue
_initialized = ContextVar("_initialized", default=False)  # Whether a server or client has been initialized

LOADING, MESSAGE, SERVER_START, \
SERVER_EXIT, CONNECTION_RESET, \
CONNECTION, CONNECTION_LOST \
= range(7)

def get_events():
    with _events_lock:
        while not _events.empty():
            yield _events.get()

class Event:
    __slots__ = (
        "type", "sock", "data"
    )
    get_events = staticmethod(get_events)
    def __init__(self, *, type, sock, data=None):
        self.type = type
        self.sock = sock
        self.data = data
    @property
    def type_name(self):
        return {
            LOADING: "LOADING",
            MESSAGE: "MESSAGE",
            SERVER_START: "SERVER_START",
            SERVER_EXIT: "SERVER_EXIT",
            CONNECTION_RESET: "CONNECTION_RESET",
            CONNECTION: "CONNECTION",
            CONNECTION_LOST: "CONNECTION_LOST"
        }.get(self.type, "UNKNOWN")

class Server:
    __slots__ = (
        "host", "port", "bufsize", "connections", "thread", "socket", "reuse_port"
    )
    get_events = staticmethod(get_events)
    def __init__(self, *, port, reuse_port = False, bufsize = 1024):
        self.host = socket.gethostname()
        self.port = port
        self.reuse_port = reuse_port
        self.bufsize = bufsize
        self.connections = {}
        self.thread = Thread(target=self._accept_connections)
    def start(self):
        assert not _initialized.get(), "Cannot create a server after a server or client has already been made"
        _initialized.set(True)
        _events.put(Event(type=LOADING, sock=None))
        self.socket = socket.create_server((self.host, self.port), reuse_port=self.reuse_port)
        _events.put(Event(type=SERVER_START, sock=self.socket))
        self.thread.start()
    def _accept_connections(self):
        try:
            while True:
                client_socket, address = self.socket.accept()
                _events.put(Event(type=CONNECTION, sock=client_socket))
                client_thread = Thread(target=self._handle_client, args=(address, client_socket,))
                self.connections[address] = (client_thread, client_socket)
                client_thread.start()
        finally:
            _events.put(Event(type=SERVER_EXIT, sock=self.socket))
    def _handle_client(self, address, client_socket):
        try:
            with client_socket:
                while True:
                    try:
                        message = client_socket.recv(self.bufsize)
                        if not message:
                            continue
                        _events.put(Event(type=MESSAGE, sock=client_socket, data=message))
                    except ConnectionResetError:
                        _events.put(Event(type=CONNECTION_RESET, sock=client_socket))
                        break
        finally:
            del self.connections[address]
            _events.put(Event(type=CONNECTION_LOST, sock=client_socket))

class Client:
    __slots__ = (
        "host", "port", "timeout", "bufsize", "thread", "socket"
    )
    get_events = staticmethod(get_events)
    def __init__(self, *, host, port, timeout=None, bufsize = 1024):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.bufsize = bufsize
        self.thread = Thread(target=self._receive_messages)
    def connect(self):
        assert not _initialized.get(), "Cannot connect to server after a client or server has already been made"
        _initialized.set(True)
        _events.put(Event(type=LOADING, sock=None))
        self.socket = socket.create_connection((self.host, self.port), self.timeout)
        _events.put(Event(type=CONNECTION, sock=self.socket))
        self.thread.start()
    def _receive_messages(self):
        try:
            with self.socket:
                while True:
                    try:
                        message = self.socket.recv(self.bufsize)
                        if not message:
                            continue
                        _events.put(Event(type=MESSAGE, sock=self.socket, data=message))
                    except ConnectionResetError:
                        _events.put(Event(type=CONNECTION_RESET, sock=self.socket))
                        break
        finally:
            _events.put(Event(type=CONNECTION_LOST, sock=self.socket))