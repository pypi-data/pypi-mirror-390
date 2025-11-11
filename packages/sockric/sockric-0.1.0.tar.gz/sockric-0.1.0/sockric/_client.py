from sockric._packet import encode, decode, decode_from_stream
from sockric._events import EventManager, EventDefaults
from sockric._utils import serialize, deserialize
from sockric._transport import TCP
import socket, threading, time, json
import loggerric as lr

class Client:
    def __init__(self, host_ip:str, port:int):
        self.__host_ip = host_ip
        self.__port = port

        self.password:str = None
        self.is_connected = False
        self.__events = EventManager()
    
        self.__socket:socket.socket = None
        self.__tcp_wrapper:TCP = None
        self.__recv_thread:threading.Thread = None

    def get_host(self) -> tuple[str, int]:
        return self.__host_ip, self.__port

    def connect(self, password:str=None) -> None:
        if self.is_connected:
            lr.Log.warn('Client is already connected!')
            return
    
        self.password = password

        lr.Log.debug(f'Client connecting to {self.__host_ip}:{self.__port}')

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.settimeout(2.0)

        try:
            self.__socket.connect((self.__host_ip, self.__port))
        except Exception as error:
            lr.Log.error(f'TCP connection failed: {error}')
            return

        self.__tcp_wrapper = TCP(self.__socket, (self.__host_ip, self.__port))

        self.is_connected = True

        self.__recv_thread = threading.Thread(target=self.__tcp_recv_loop, daemon=True)
        self.__recv_thread.start()

        lr.Log.info('Client successfully connected (awaiting handshake confirmation)')

        handshake = { 'password': self.password }
        frame = encode('__handshake__', handshake)
        try:
            self.__tcp_wrapper.send(frame)
        except Exception as error:
            lr.Log.error(f'Handshake send failed: {error}')
    
    def send(self, packet_id:str, data):
        if not self.is_connected:
            lr.Log.warn('Cannot send while client not connected!')
            return
        
        frame = encode(packet_id, data)

        try:
            self.__tcp_wrapper.send(frame)
        except Exception as error:
            lr.Log.error(f'TCP send error: {error}')

    def disconnect(self):
        if not self.is_connected:
            lr.Log.warn("Client isn't connected!")
            return

        lr.Log.info("Client disconnecting!")
        self.is_connected = False

        try:
            if self.__tcp_wrapper and not self.__tcp_wrapper.closed:
                # Send a disconnect packet first
                try:
                    frame = encode('__disconnect__', None)
                    self.__tcp_wrapper.send(frame)
                    time.sleep(0.1)  # Give server time to process
                except Exception:
                    pass
                self.__tcp_wrapper.close()
        except Exception as e:
            lr.Log.warn(f"Error closing TCP: {e}")

        if self.__recv_thread and self.__recv_thread.is_alive():
            self.__recv_thread.join(timeout=1.0)

    def on_packet(self, id:str) -> None:
        def decorator(func):
            self.__events.register(id, func)
            return func
        
        return decorator

    def __tcp_recv_loop(self) -> None:
        lr.Log.debug('Client TCP recv loop started!')

        while self.is_connected:
            try:
                response = decode_from_stream(self.__tcp_wrapper)
                if response is None:
                    continue
                    
                if response == b'':
                    lr.Log.info('Server closed TCP connection')
                    break

                header, payload = response

                # Check if this is the handshake response
                packet_id = header.get('id')
                if packet_id == '__auth_success__':
                    lr.Log.info('Handshake authentication passed!')
                elif packet_id == '__auth_failed__':
                    lr.Log.info('Handshake authentication failed!')
                    break

                data = deserialize(header.get('content_type'), payload)
                self.__events.trigger(packet_id, { 'data': data, 'header': header })
            except Exception as error:
                lr.Log.error(f'Client TCP recv loop error: {error}')
                break
        
        self.disconnect()