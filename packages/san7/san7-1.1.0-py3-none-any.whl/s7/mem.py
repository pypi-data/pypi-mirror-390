import sys
import gc
import threading
import hashlib


class MemoryProtection:
    def __init__(self):
        self.protected_data = {}
        self.data_hashes = {}
        self.lock = threading.Lock()
        self.monitoring = False
        self.monitor_thread = None
    
    def protect(self, key, value):
        serialized = str(value).encode()
        hash_val = hashlib.sha256(serialized).digest()
        self.protected_data[key] = value
        self.data_hashes[key] = hash_val
    
    def verify(self, key):
        if key not in self.protected_data:
            return False
        
        value = self.protected_data[key]
        serialized = str(value).encode()
        current_hash = hashlib.sha256(serialized).digest()
        
        return current_hash == self.data_hashes.get(key)
    
    def get(self, key):
        if not self.verify(key):
            return None
        return self.protected_data.get(key)
    
    def start_monitoring(self):
        pass
    
    def _monitor_loop(self):
        while self.monitoring:
            try:
                with self.lock:
                    for key in list(self.protected_data.keys()):
                        if not self.verify(key):
                            self.monitoring = False
                            return False
                threading.Event().wait(5)
            except:
                continue
        return True
    
    def stop_monitoring(self):
        self.monitoring = False
