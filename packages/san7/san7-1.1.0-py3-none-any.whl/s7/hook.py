import sys
import builtins
import threading


class SystemHooks:
    def __init__(self):
        self.hooks_active = False
        self.blocked_modules = {
            'pdb', 'ipdb', 'pudb', 'pydevd', 
            'debugpy', 'winpdb', 'rpdb'
        }
        self.original_import = None
        self.lock = threading.Lock()
    
    def activate(self):
        if not self.hooks_active:
            with self.lock:
                self.original_import = builtins.__import__
                builtins.__import__ = self._hooked_import
                self.hooks_active = True
    
    def _hooked_import(self, name, *args, **kwargs):
        if name in self.blocked_modules:
            raise ImportError(f"Module {name} is restricted")
        
        for blocked in self.blocked_modules:
            if name.startswith(blocked + '.'):
                raise ImportError(f"Module {name} is restricted")
        
        if self.original_import is not None:
            return self.original_import(name, *args, **kwargs)
        return builtins.__import__(name, *args, **kwargs)
    
    def deactivate(self):
        if self.hooks_active:
            with self.lock:
                if self.original_import:
                    builtins.__import__ = self.original_import
                self.hooks_active = False
