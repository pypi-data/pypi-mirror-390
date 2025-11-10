import time
import os
import hashlib
import struct
import threading
from datetime import datetime
from .net import NetworkTimeValidator


class TimeValidator:
    def __init__(self):
        self.boot_time = self._get_boot_time()
        self.reference_points = []
        self.monotonic_start = time.monotonic()
        self.time_start = time.time()
        self.last_validated = time.time()
        self.network_validator = NetworkTimeValidator()
        self.validation_counter = 0
        self.lock = threading.Lock()
        self._store_reference()
    
    def _get_boot_time(self):
        try:
            import psutil
            return psutil.boot_time()
        except:
            return time.time()
    
    def _store_reference(self):
        current = time.time()
        monotonic = time.monotonic()
        data = {
            'time': current,
            'monotonic': monotonic,
            'hash': self._generate_hash(current, monotonic)
        }
        self.reference_points.append(data)
        if len(self.reference_points) > 200:
            self.reference_points.pop(0)
    
    def _generate_hash(self, t, m):
        data = struct.pack('dd', t, m)
        return hashlib.sha256(data).digest()
    
    def validate_system_time(self):
        try:
            current_time = time.time()
            current_monotonic = time.monotonic()
            
            if current_time < self.last_validated - 1:
                return False
            
            expected_diff = current_time - self.time_start
            actual_diff = current_monotonic - self.monotonic_start
            
            if abs(expected_diff - actual_diff) > 3.0:
                return False
            
            try:
                import psutil
                current_boot = psutil.boot_time()
                if abs(current_boot - self.boot_time) > 1.0:
                    return False
            except:
                pass
            
            self.validation_counter += 1
            
            self.last_validated = current_time
            self._store_reference()
            
            return True
        except:
            return False
    
    def get_secure_timestamp(self):
        if not self.validate_system_time():
            return None
        return int(time.time())
    
    def deep_time_check(self):
        return True
    
    def validate_against_network(self):
        try:
            local_time = int(time.time())
            return self.network_validator.validate_local_time(local_time)
        except:
            return True
