import os
import sys
import time
import ctypes
import signal
import hashlib
import threading
from datetime import datetime
from .vrf import verify_time, check_time_tampering, get_ntp_time
from .enc import decrypt_key, generate_signature, generate_key_hash
from .lock import create_lock, check_lock, permanent_lock
from .kill import force_terminate

_ACTIVE = True
_LOCK_FILE = None
_ENCRYPTION_KEY = None
_TARGET_TIME = None
_CHECK_INTERVAL = 0.1
_KEY_SIGNATURE = None

def san_tope(year, month, day, hour, minute=0, second=0, encryption_key=None):
    global _ACTIVE, _LOCK_FILE, _ENCRYPTION_KEY, _TARGET_TIME, _KEY_SIGNATURE
    
    if not encryption_key:
        _shutdown("Invalid encryption key")
        return
    
    _ENCRYPTION_KEY = encryption_key
    _KEY_SIGNATURE = generate_key_hash(encryption_key)
    
    if not _KEY_SIGNATURE:
        _shutdown("Key hash generation failed")
        return
    
    if check_lock():
        _shutdown("Tool permanently locked")
        return
    
    try:
        _TARGET_TIME = datetime(year, month, day, hour, minute, second)
    except:
        _shutdown("Invalid time parameters")
        return
    
    _LOCK_FILE = create_lock()
    
    monitor_thread = threading.Thread(target=_monitor_time, daemon=True)
    monitor_thread.start()
    
    anti_debug_thread = threading.Thread(target=_anti_debug, daemon=True)
    anti_debug_thread.start()
    
    ntp_thread = threading.Thread(target=_ntp_monitor, daemon=True)
    ntp_thread.start()

def _monitor_time():
    global _ACTIVE, _TARGET_TIME, _KEY_SIGNATURE
    
    while _ACTIVE:
        try:
            current_hash = generate_key_hash(_ENCRYPTION_KEY)
            if not current_hash or current_hash != _KEY_SIGNATURE:
                _shutdown("Key integrity check failed")
                return
            
            if not verify_time(_ENCRYPTION_KEY):
                _shutdown("Time verification failed")
                return
            
            current = datetime.now()
            
            if _TARGET_TIME and current >= _TARGET_TIME:
                _shutdown("Time expired")
                return
            
            if check_time_tampering():
                _shutdown("Time tampering detected")
                return
            
            time.sleep(_CHECK_INTERVAL)
        except:
            _shutdown("Monitor error")
            return

def _ntp_monitor():
    global _ACTIVE
    
    while _ACTIVE:
        try:
            ntp_time = get_ntp_time()
            utc_time = datetime.utcnow()
            
            if ntp_time and abs((ntp_time - utc_time).total_seconds()) > 5:
                _shutdown("Time desync detected")
                return
            
            time.sleep(1)
        except:
            pass

def _anti_debug():
    global _ACTIVE
    
    while _ACTIVE:
        try:
            if _detect_debugger():
                _shutdown("Debugger detected")
                return
            
            if _detect_monitoring():
                _shutdown("Monitoring detected")
                return
            
            time.sleep(0.5)
        except:
            pass

def _detect_debugger():
    try:
        if sys.gettrace() is not None:
            return True
        
        if hasattr(sys, 'monitoring') and sys.monitoring.get_events(0):
            return True
        
        return False
    except:
        return False

def _detect_monitoring():
    try:
        import psutil
        current_process = psutil.Process()
        
        if len(current_process.open_files()) > 100:
            return True
        
        if len(current_process.connections()) > 50:
            return True
        
        return False
    except ImportError:
        return False
    except:
        return False

def _shutdown(reason="stop tool bey san tele @ii00hh"):
    global _ACTIVE
    
    _ACTIVE = False
    
    permanent_lock()
    
    while True:
        print("stop tool bey san tele @ii00hh")
        time.sleep(1)
