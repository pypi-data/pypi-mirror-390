from sockric._packet import encode, decode, decode_from_stream
from sockric._events import EventManager, EventDefaults
from sockric._utils import serialize, deserialize
from sockric._transport import TCP
import socket, threading, time, json
import loggerric as lr

class Server:
    def __init__(self, host_ip:str, port:int, password:str=None):
        # Expand parameters scopes
        self.__host_ip = host_ip
        self.__port = port
        self.password = password
    
        self.__is_running = False
        self.__client_id_counter = 0
        self.__clients:dict[int, dict] = {}
        self.__events = EventManager()

        self.__tcp_socket:socket.socket = None
        self.__clients_lock:threading.Lock = None
        self.__recv_threads:list[threading.Thread] = None
        self.__accept_thread:threading.Thread = None

    def get_host(self) -> tuple[str, int]:
        return self.__host_ip, self.__port

    def start(self) -> None:
        # Check if the server is already running
        if self.__is_running:
            lr.Log.warn('Server is already running!')
            return
        
        lr.Log.debug(f'Starting server, hosting on: {self.__host_ip}:{self.__port}')

        # Set up the TCP socket as a server
        self.__tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__tcp_socket.bind((self.__host_ip, self.__port))
        self.__tcp_socket.listen(8) # Queue size

        self.__is_running = True
        self.__clients_lock = threading.Lock()
        self.__recv_threads:dict[int, threading.Thread] = {}

        # Set up the client accept thread
        self.__accept_thread = threading.Thread(target=self.__client_accept_loop, daemon=True)
        self.__accept_thread.start()

        lr.Log.info(f'Server successfully started, hosting on ({self.__host_ip}:{self.__port})')

    def stop(self) -> None:
        # Check if the server is running
        if not self.__is_running:
            lr.Log.warn('Server is not running!')
            return

        self.broadcast(EventDefaults.SERVER_STOPPED, '__server_stopped__')

        self.__is_running = False

        lr.Log.debug('Stopping server!')

    def send(self, packet_id:str, client_ids:int|list, data) -> None:
        if isinstance(client_ids, int):
            client_ids = [client_ids]
        
        frame = encode(packet_id, data)
        with self.__clients_lock:
            for client_id, info in self.__clients.items():
                if client_ids and client_id not in client_ids:
                    continue

                try:
                    tcp:TCP = info.get('tcp')
                    tcp.send(frame)
                except Exception as error:
                    lr.Log.error(f'Failed to send to client {client_id}: {error}')

    def broadcast(self, packet_id:str, data, exclude_clients:list[int]=None) -> None:
        if exclude_clients is None:
            exclude_clients = []
        
        with self.__clients_lock:
            for client_id in list(self.__clients.keys()):
                if client_id in exclude_clients:
                    continue

                self.send(packet_id, client_id, data)

    def on_packet(self, id:str):
        def decorator(func):
            self.__events.register(id, func)
            return func
        
        return decorator

    def __client_accept_loop(self) -> None:
        lr.Log.debug('Client accepting loop started!')

        def attempt_accecpt():
            connection, address = self.__tcp_socket.accept()
            lr.Log.debug(f'Incomming TCP connection from: {address}')

            tcp_wrapper = TCP(connection, address)

            response:tuple[dict, dict] = None
            try:
                response = decode_from_stream(tcp_wrapper)
            except Exception as error:
                lr.Log.warn(f'Handshake decode error: {error}')
            
            if response == b'':
                lr.Log.warn('Connection closed by peer during handshake!')
                tcp_wrapper.close()
                return
            else:
                header, payload = response
                meta:dict = deserialize(header.get('content_type'), payload)

                password = meta.get('password')
                if header.get('id') == '__handshake__':
                    if self.password and self.password != password:
                        lr.Log.info(f'Rejecting connection from {address}: "{password}" Incorrect password!')

                        failure = encode('__auth_failed__', { 'reason': 'bad_password' })
                        tcp_wrapper.send(failure)
                        tcp_wrapper.close()
                        return
                    else:
                        success = encode('__auth_success__', { 'reason': ('good_password' if self.password else 'no_password_set') })
                        tcp_wrapper.send(success)
            
            with self.__clients_lock:
                client_id = self.__client_id_counter
                self.__client_id_counter += 1
                self.__clients[client_id] = { 'tcp': tcp_wrapper, 'address': address }
            
            lr.Log.info(f'Client {client_id} connected from: {address}')

            self.__events.trigger(EventDefaults.CLIENT_CONNECTED, { 'client_id': client_id, 'address': address })

            thread = threading.Thread(target=self.__tcp_client_loop, args=(client_id,), daemon=True)
            thread.start()
            self.__recv_threads[client_id] = thread
        while self.__is_running:
            try:
                attempt_accecpt()
            except Exception as error:
                if self.__is_running:
                    lr.Log.error(f'Accept loop error: {error}')

    def __tcp_client_loop(self, client_id:int) -> None:
        lr.Log.debug(f'TCP recv loop for client {client_id} started!')

        tcp_wrapper = None
        with self.__clients_lock:
            info = self.__clients.get(client_id)
            if not info:
                return
            
            tcp_wrapper = info.get('tcp')
        
        while self.__is_running:
            try:
                response = decode_from_stream(tcp_wrapper)
                if response is None:
                    continue

                if response == b'':
                    lr.Log.debug(f'Client {client_id} disconnected')
                    break

                header, payload = response
                packet_id = header.get('id')
                
                # Handle graceful disconnect packet
                if packet_id == '__disconnect__':
                    lr.Log.debug(f'Client {client_id} sent disconnect packet')
                    break

                header, payload = response
                data = deserialize(header.get('content_type'), payload)
                self.__events.trigger(header.get('id'), { 'client_id': client_id, 'data': data, 'header': header })
            except Exception as error:
                lr.Log.error(f'Error in TCP recv loop for client {client_id}: {error}')
                break
        
        self.__cleanup_client(client_id)
    
    def __cleanup_client(self, client_id:int) -> None:
        with self.__clients_lock:
            client_info = self.__clients.pop(client_id, None)
            client_thread = self.__recv_threads.pop(client_id, None)
        
        if not client_info:
            lr.Log.warn(f'Attempted to clean up non-existent client {client_id}')
            return
            
        # Trigger disconnect event with client info
        self.__events.trigger(EventDefaults.CLIENT_DISCONNECTED, {'client_id': client_id, 'address': client_info.get('tcp').address})
        
        if client_thread and threading.current_thread() != client_thread:
            try:
                client_thread.join(1.0)
            except Exception as error:
                lr.Log.error(f'Error while joining client {client_id} thread: {error}')

        tcp_wrapper:TCP = client_info.get('tcp')
        if tcp_wrapper:
            try:
                tcp_wrapper.close()
                lr.Log.info(f'Closed TCP socket for client {client_id}')
            except Exception as error:
                lr.Log.warn(f'Error closing TCP socket for client {client_id}: {error}')