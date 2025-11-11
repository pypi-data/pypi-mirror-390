import socket, threading, time, json
import loggerric as lr

class TCP:
    def __init__(self, connection:socket.socket, address:tuple[str, int]):
        # Expand parameters scopes
        self.connection = connection
        self.address = address

        self.connection.settimeout(1)

        self.closed = False

        # Thread locks
        self.__recv_lock = threading.Lock()
        self.__send_lock = threading.Lock()
    
    def send(self, raw_bytes:bytes) -> None:
        if self.closed:
            lr.Log.warn('Attempt to send on closed TCP!')
            return
        
        try:
            with self.__send_lock:
                total_sent = 0
                while total_sent < len(raw_bytes):
                    sent = self.connection.send(raw_bytes[total_sent:])

                    if sent == 0:
                        raise RuntimeError('Socket connection broken')

                    total_sent += sent
        except Exception as error:
            lr.Log.error(f'TCP send error to {self.address}: {error}')
            self.close()

    def receive(self, num_bytes:int) -> bytes | None:
        data = bytearray()

        try:
            while len(data) < num_bytes:
                try:
                    chunk = self.connection.recv(num_bytes - len(data))
                except socket.timeout:
                    # No data yet — just return None to let higher-level loop continue
                    return None

                if chunk == b'':
                    # The peer gracefully closed the connection
                    return b''

                data.extend(chunk)

            return bytes(data)
        
        except (ConnectionResetError, OSError) as error:
            lr.Log.warn(f'TCP connection error from {self.address}: {error}')
            self.close()
            return b''
        except Exception as error:
            lr.Log.error(f'Unexpected TCP receive error from {self.address}: {error}')
            self.close()
            return b''

    def close(self) -> None:
        if self.closed:
            return
        
        self.closed = True

        try:
            self.connection.shutdown(socket.SHUT_RDWR)
        except:
            pass

        try:
            self.connection.close()
        except:
            pass