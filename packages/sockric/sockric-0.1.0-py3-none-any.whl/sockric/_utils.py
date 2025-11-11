import socket, threading, time, json, pickle, math
import loggerric as lr

def serialize(data) -> tuple[str, bytes]:
    if isinstance(data, (bytes, bytearray)):
        return 'bytes', bytes(data)

    try:
        j = json.dumps(data, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
        return 'json', j
    except Exception as error:
        lr.Log.debug(f'JSON serialization failed: {error}, faling back to pickle.')

        p = pickle.dumps(data)
        return 'pickle', p

def deserialize(content_type:str, payload_bytes:bytes) -> bytes:
    if content_type == 'bytes':
        return payload_bytes
    
    if content_type == 'json':
        try:
            return json.loads(payload_bytes.decode('utf-8'))
        except Exception as error:
            lr.Log.error(f'Failed JSON decode: {error}')
            return
    
    if content_type == 'pickle':
        try:
            return pickle.loads(payload_bytes)
        except Exception as error:
            lr.Log.error(f'Failed pickle loads: {error}')
            return
        
    lr.Log.warn(f'Unknown content type: "{content_type}"')