import sys
import os
import platform
import threading

_TERMINATED = False

def force_terminate():
    global _TERMINATED
    _TERMINATED = True
    
    try:
        sys.stdout.flush()
        sys.stderr.flush()
    except:
        pass
    
    threading.Thread(target=_hard_stop, daemon=False).start()

def _hard_stop():
    import time
    time.sleep(0.5)
    
    try:
        if platform.system() != 'Windows':
            import signal
            os.kill(os.getpid(), signal.SIGTERM)
    except:
        pass
    
    try:
        raise SystemExit(0)
    except:
        pass
    
    try:
        os._exit(0)
    except:
        pass

def is_terminated():
    return _TERMINATED
