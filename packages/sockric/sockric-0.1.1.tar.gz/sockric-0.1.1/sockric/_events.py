import socket, threading, time, json
from collections import defaultdict
import loggerric as lr
from enum import Enum

class EventDefaults(Enum):
    CLIENT_CONNECTED = 'client_connected'           # Server
    CLIENT_DISCONNECTED = 'client_disconnected'     # Server
    SERVER_STOPPED = 'server_stopped'               # Client
    UNKNOWN_ID = 'unknown_id'                       # Both

class EventManager:
    def __init__(self):
        self.__handlers = defaultdict(list)
        self.__lock = threading.Lock()
    
    def register(self, event_id:str, func) -> None:
        with self.__lock:
            self.__handlers[event_id].append(func)
            lr.Log.debug(f'Registered handler "{func}" for event "{event_id}"')

    def unregister(self, event_id:str, func) -> None:
        with self.__lock:
            handlers = self.__handlers.get(event_id)
            if handlers and func in handlers:
                handlers.remove(func)
                lr.Log.debug(f'Unregistered handler "{func}" for event "{event_id}"')
    
    def trigger(self, event_id:str, data) -> None:
        handlers = []
        with self.__lock:
            handlers = list(self.__handlers.get(event_id, []))

        if len(handlers) == 0:
            handlers = list(self.__handlers.get(EventDefaults.UNKNOWN_ID, []))

        for func in handlers:
            try:
                func(data)
            except Exception as error:
                lr.Log.error(f'Event handler for "{event_id}" raised: {error}')