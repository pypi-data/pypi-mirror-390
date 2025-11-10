import os
import sys
import time
import threading
import hashlib
import psutil
from datetime import datetime
from .mem import MemoryProtection
from .hook import SystemHooks


class ProtectionSystem:
    def __init__(self):
        self.monitoring_active = False
        self.expire_time = None
        self.process = psutil.Process()
        self.initial_pid = os.getpid()
        self.parent_pid = os.getppid()
        self.creation_time = self.process.create_time()
        self.monitor_thread = None
        self.system_locked = False
        self._detection_count = 0
        self.memory_protection = MemoryProtection()
        self.system_hooks = SystemHooks()
        self.check_sequence = []
        
    def register_expiration(self, timestamp):
        self.expire_time = timestamp
        self.memory_protection.protect('expire_time', timestamp)
        self.memory_protection.protect('initial_pid', self.initial_pid)
    
    def start_monitoring(self):
        pass
    
    def _monitor_loop(self):
        last_check = time.time()
        check_interval = 0.5
        iteration = 0
        
        while self.monitoring_active:
            try:
                current_time = time.time()
                iteration += 1
                
                if current_time - last_check > check_interval * 5:
                    self._handle_detection("TIME_MANIPULATION")
                
                if iteration % 2 == 0:
                    if not self._verify_process_integrity():
                        self._handle_detection("PROCESS_MANIPULATION")
                
                if iteration % 3 == 0:
                    if not self._check_debugger():
                        self._handle_detection("DEBUGGER_DETECTED")
                
                if iteration % 4 == 0:
                    if not self._verify_memory_integrity():
                        self._handle_detection("MEMORY_TAMPERING")
                
                if self.expire_time and current_time >= self.expire_time:
                    self.lock_system()
                    from .term import SystemTerminator
                    terminator = SystemTerminator()
                    terminator.terminate_with_message()
                
                self.check_sequence.append(current_time)
                if len(self.check_sequence) > 100:
                    self.check_sequence.pop(0)
                
                last_check = current_time
                time.sleep(check_interval)
                
            except:
                continue
    
    def _verify_process_integrity(self):
        try:
            if os.getpid() != self.initial_pid:
                return False
            
            stored_pid = self.memory_protection.get('initial_pid')
            if stored_pid and stored_pid != self.initial_pid:
                return False
            
            if os.getppid() != self.parent_pid:
                return False
            
            if abs(self.process.create_time() - self.creation_time) > 0.1:
                return False
            
            return True
        except:
            return False
    
    def _verify_memory_integrity(self):
        try:
            if not self.memory_protection.verify('expire_time'):
                return False
            
            if not self.memory_protection.verify('initial_pid'):
                return False
            
            return True
        except:
            return False
    
    def _check_debugger(self):
        try:
            if sys.gettrace() is not None:
                return False
            
            if hasattr(sys, 'getprofile') and sys.getprofile() is not None:
                return False
            
            try:
                import ctypes
                if hasattr(ctypes, 'windll'):
                    if ctypes.windll.kernel32.IsDebuggerPresent():
                        return False
            except:
                pass
            
            try:
                with open('/proc/self/status', 'r') as f:
                    for line in f:
                        if line.startswith('TracerPid:'):
                            pid = int(line.split(':')[1].strip())
                            if pid != 0:
                                return False
            except:
                pass
            
            return True
        except:
            return True
    
    def _handle_detection(self, reason):
        self._detection_count += 1
        if self._detection_count >= 2:
            self.lock_system()
            from .term import SystemTerminator
            terminator = SystemTerminator()
            terminator.emergency_shutdown(reason)
    
    def lock_system(self):
        self.system_locked = True
        self.monitoring_active = False
        self.memory_protection.stop_monitoring()
        self.system_hooks.deactivate()
