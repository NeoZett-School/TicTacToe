"""This module provides a simple interface for creating a 
server and client that can communicate over a 
network using sockets. 

The Server class listens for incoming connections 
and handles them in separate threads, while the 
Client class connects to a server and receives 
messages in a separate thread. 

The Event class represents an event that occurs 
in the network, such as a message being received 
or a connection being reset. The get_events 
function returns a list of all events that 
have occurred in the network."""

from typing import Optional, Generator, Tuple, Dict, Self, Any
from threading import Thread
import socket

LOADING, MESSAGE, SERVER_START, \
SERVER_EXIT, CONNECTION_RESET, \
CONNECTION, CONNECTION_LOST \
= range(7)

def get_events() -> Generator[Event, Any, None]: 
    """Returns a list of all events that have occurred in the network.
    
    Returns:
        A list of Event objects representing all events that have occurred in the network.
    """

class Event:
    """The event class represents an event that occurs in the network, such as a message being received or a connection being reset."""

    type: int
    sock: socket.socket
    data: Optional[Any]

    def __init__(self: Self, *, type: int, sock: socket.socket, data: Optional[Any] = None) -> None: ...
    @staticmethod
    def get_events() -> Generator[Event, Any, None]: 
        """Returns a list of all events that have occurred in the network.
        
        Returns:
            A list of Event objects representing all events that have occurred in the network.
        """
    @property
    def type_name(self: Self) -> str: ...

class Server:
    """The Server class represents a server that listens for incoming connections and handles them in separate threads."""

    host: str
    port: int
    reuse_port: bool
    bufsize: int
    connections: Dict[socket._Address, Tuple[Thread, socket.socket]]
    thread: Thread
    socket: socket.socket

    def __init__(self: Self, *, port: int, reuse_port: bool = False, bufsize: int = 1024) -> None: ...
    @staticmethod
    def get_events() -> Generator[Event, Any, None]: 
        """Returns a list of all events that have occurred in the network.
        
        Returns:
            A list of Event objects representing all events that have occurred in the network.
        """
    def start(self: Self) -> None: ...

class Client:
    """The Client class represents a client that connects to a server and receives messages in a separate thread."""
    
    host: str
    port: int
    timeout: Optional[float]
    bufsize: int
    thread: Thread
    socket: socket.socket

    def __init__(self: Self, *, host: str, port: int, timeout: Optional[float] = None, bufsize: int = 1024) -> None: ...
    @staticmethod
    def get_events() -> Generator[Event, Any, None]: 
        """Returns a list of all events that have occurred in the network.
        
        Returns:
            A list of Event objects representing all events that have occurred in the network.
        """
    def connect(self: Self) -> None: ...