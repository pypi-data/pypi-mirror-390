import socket, threading, time, json, struct
from sockric._utils import serialize
from sockric._transport import TCP
import loggerric as lr

HEADER_LENGTH_FMT = '!I' # 4 Bytes

def encode(packet_id:str, data, extra_meta:dict=None) -> bytes:
    content_type, payload = serialize(data)

    header = { 'id': packet_id, 'content_type': content_type, 'payload_length': len(payload) }

    if extra_meta:
        header.update(extra_meta)
    
    header_bytes = json.dumps(header, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    frame = struct.pack(HEADER_LENGTH_FMT, len(header_bytes)) + header_bytes + payload

    return frame

def decode(raw_bytes:bytes) -> tuple[dict, bytes]:
    print('decode')

def decode_from_stream(socket_wrapper:TCP) -> tuple[dict, bytes]:
    header:dict = socket_wrapper.receive(4)
    if header is None:
        return
    
    if header == b'':
        return b''
    
    if len(header) < 4:
        lr.Log.error('Short header length received!')
        return b''
    
    header_length = struct.unpack(HEADER_LENGTH_FMT, header)[0]
    header_bytes = socket_wrapper.receive(header_length)

    if header_bytes is None:
        return
    
    if header_bytes == b'':
        return b''
    
    header = json.loads(header_bytes.decode('utf-8'))
    payload_length = header.get('payload_length', 0)
    payload = b''
    
    if payload_length > 0:
        payload = socket_wrapper.receive(payload_length)
        if payload is None:
            return
        if payload == b'':
            return b''
    
    return header, payload