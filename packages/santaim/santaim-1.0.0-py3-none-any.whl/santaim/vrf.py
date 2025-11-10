import os
import time
import socket
import struct
import hashlib
import requests
from datetime import datetime, timedelta

_LAST_TIME = None
_TIME_CHECKS = []
_NTP_SERVERS = [
    'time.google.com',
    'time.cloudflare.com',
    'pool.ntp.org',
    'time.nist.gov',
    'time.windows.com'
]

_TIME_API_URLS = [
    'https://worldtimeapi.org/api/ip',
    'https://timeapi.io/api/Time/current/zone?timeZone=UTC'
]

def verify_time(encryption_key):
    try:
        current = datetime.now()
        
        sig = hashlib.sha256(f"{current.isoformat()}{encryption_key}".encode()).hexdigest()
        
        if not _check_time_progression(current):
            return False
        
        return True
    except:
        return False

def _check_time_progression(current):
    global _LAST_TIME
    
    if _LAST_TIME is None:
        _LAST_TIME = current
        return True
    
    if current < _LAST_TIME:
        return False
    
    diff = (current - _LAST_TIME).total_seconds()
    
    if diff > 10:
        return False
    
    _LAST_TIME = current
    return True

def check_time_tampering():
    global _TIME_CHECKS
    
    current = time.time()
    _TIME_CHECKS.append(current)
    
    if len(_TIME_CHECKS) > 10:
        _TIME_CHECKS.pop(0)
    
    if len(_TIME_CHECKS) >= 3:
        for i in range(len(_TIME_CHECKS) - 1):
            diff = _TIME_CHECKS[i + 1] - _TIME_CHECKS[i]
            if diff < 0 or diff > 5:
                return True
    
    return False

def get_ntp_time():
    for server in _NTP_SERVERS:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client.settimeout(2)
            
            data = b'\x1b' + 47 * b'\0'
            client.sendto(data, (server, 123))
            
            response, _ = client.recvfrom(1024)
            client.close()
            
            if len(response) >= 48:
                t = struct.unpack('!12I', response)[10]
                t -= 2208988800
                return datetime.utcfromtimestamp(t)
        except:
            continue
    
    return None

def get_api_time():
    for url in _TIME_API_URLS:
        try:
            response = requests.get(url, timeout=3, verify=True)
            if response.status_code == 200:
                data = response.json()
                
                if 'datetime' in data:
                    time_str = data['datetime'].split('.')[0]
                    return datetime.fromisoformat(time_str.replace('Z', ''))
                elif 'dateTime' in data:
                    return datetime.fromisoformat(data['dateTime'].split('.')[0])
                elif 'currentDateTime' in data:
                    return datetime.fromisoformat(data['currentDateTime'].split('.')[0])
        except:
            continue
    
    return None
