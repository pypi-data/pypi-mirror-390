import os
import sys
import json
import hashlib
import platform
from pathlib import Path
from datetime import datetime

def _get_lock_path():
    system = platform.system()
    
    if system == 'Windows':
        base = os.path.join(os.environ.get('APPDATA', ''), '.santaim')
    elif system == 'Darwin':
        base = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', '.santaim')
    else:
        base = os.path.join(os.path.expanduser('~'), '.config', '.santaim')
    
    os.makedirs(base, exist_ok=True)
    
    machine_id = _get_machine_id()
    lock_file = os.path.join(base, f'.lck_{machine_id}')
    
    return lock_file

def _get_machine_id():
    try:
        if platform.system() == 'Windows':
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r'SOFTWARE\Microsoft\Cryptography')
            guid = winreg.QueryValueEx(key, 'MachineGuid')[0]
            winreg.CloseKey(key)
            return hashlib.sha256(guid.encode()).hexdigest()[:16]
        elif platform.system() == 'Darwin':
            import subprocess
            result = subprocess.check_output(['ioreg', '-rd1', '-c', 'IOPlatformExpertDevice'])
            for line in result.decode().split('\n'):
                if 'IOPlatformUUID' in line:
                    uuid = line.split('"')[-2]
                    return hashlib.sha256(uuid.encode()).hexdigest()[:16]
        else:
            machine_id = '/etc/machine-id'
            if os.path.exists(machine_id):
                with open(machine_id, 'r') as f:
                    mid = f.read().strip()
                    return hashlib.sha256(mid.encode()).hexdigest()[:16]
    except:
        pass
    
    return hashlib.sha256(f"{platform.node()}{os.getpid()}".encode()).hexdigest()[:16]

def create_lock():
    lock_path = _get_lock_path()
    
    if not os.path.exists(lock_path):
        data = {
            'created': datetime.now().isoformat(),
            'machine': _get_machine_id(),
            'locked': False
        }
        
        with open(lock_path, 'w') as f:
            json.dump(data, f)
    
    return lock_path

def check_lock():
    lock_path = _get_lock_path()
    
    if not os.path.exists(lock_path):
        return False
    
    try:
        with open(lock_path, 'r') as f:
            data = json.load(f)
        
        return data.get('locked', False)
    except:
        return False

def permanent_lock():
    lock_path = _get_lock_path()
    
    try:
        data = {
            'created': datetime.now().isoformat(),
            'machine': _get_machine_id(),
            'locked': True,
            'locked_time': datetime.now().isoformat()
        }
        
        with open(lock_path, 'w') as f:
            json.dump(data, f)
        
        if platform.system() != 'Windows':
            os.chmod(lock_path, 0o444)
    except:
        pass
