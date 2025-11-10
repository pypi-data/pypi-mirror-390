import os
import sys
import time
import hashlib
import pickle
import struct
import threading
from datetime import datetime
from .prot import ProtectionSystem
from .val import TimeValidator
from .term import SystemTerminator
from .mem import MemoryProtection


class ExpireDate:
    _instance = None
    _initialized = False
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not ExpireDate._initialized:
            with ExpireDate._lock:
                if not ExpireDate._initialized:
                    self.protection = ProtectionSystem()
                    self.validator = TimeValidator()
                    self.terminator = SystemTerminator()
                    self.memory = MemoryProtection()
                    self.expire_timestamp = None
                    self.checksum = None
                    self.last_check = 0
                    self.check_counter = 0
                    self._lock_state = False
                    self._check_history = []
                    ExpireDate._initialized = True
    
    def set_date(self, year, month, day, hour=23, minute=59, second=59):
        try:
            target_date = datetime(year, month, day, hour, minute, second)
            self.expire_timestamp = int(target_date.timestamp())
            self._store_encrypted()
            self.memory.protect('expire_ts', self.expire_timestamp)
            self.protection.register_expiration(self.expire_timestamp)
            self.protection.start_monitoring()
            return True
        except:
            self.terminator.emergency_shutdown("INVALID_DATE")
            return False
    
    def _store_encrypted(self):
        data = struct.pack('Q', self.expire_timestamp)
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha512', data, salt, 100000)
        self.checksum = hashlib.sha3_512(key + data).digest()
        encrypted = bytes(a ^ b for a, b in zip(data, key[:8]))
        self._hidden_data = (encrypted, salt, self.checksum)
        
        additional_data = struct.pack('QQ', self.expire_timestamp, int(time.time()))
        self._backup_checksum = hashlib.sha256(additional_data).digest()
    
    def _verify_integrity(self):
        if not hasattr(self, '_hidden_data'):
            return False
        
        encrypted, salt, stored_checksum = self._hidden_data
        data = struct.pack('Q', self.expire_timestamp)
        key = hashlib.pbkdf2_hmac('sha512', data, salt, 100000)
        calculated_checksum = hashlib.sha3_512(key + data).digest()
        
        return calculated_checksum == stored_checksum
    
    def check(self):
        if self._lock_state:
            self.terminator.terminate_with_message()
            return False
        
        if self.expire_timestamp is None:
            return True
        
        current_time = int(time.time())
        
        if hasattr(self, '_hidden_data'):
            if not self._verify_integrity():
                self.terminator.emergency_shutdown("TAMPERING_DETECTED")
                return False
        
        if current_time < self.last_check - 5:
            self.terminator.emergency_shutdown("TIME_REVERSAL")
            return False
        
        if current_time >= self.expire_timestamp:
            self._lock_state = True
            self.terminator.terminate_with_message()
            return False
        
        self.check_counter += 1
        self.last_check = current_time
        
        return True


_global_expire = None
_global_lock = threading.Lock()


def set_expiration(year, month, day, hour=23, minute=59, second=59):
    global _global_expire
    if _global_expire is None:
        _global_expire = ExpireDate()
    return _global_expire.set_date(year, month, day, hour, minute, second)


def check_expiration():
    global _global_expire
    if _global_expire is None:
        return True
    return _global_expire.check()
