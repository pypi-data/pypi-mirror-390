import os
import sys
import time
import signal
import threading
import ctypes


class SystemTerminator:
    _terminated = False
    _lock = threading.Lock()
    
    def __init__(self):
        self.message = "by san"
        self.shutdown_delay = 0.05
    
    def terminate_with_message(self):
        with SystemTerminator._lock:
            if SystemTerminator._terminated:
                return
            SystemTerminator._terminated = True
        
        self._display_notice()
        self._intelligent_shutdown()
    
    def emergency_shutdown(self, reason):
        with SystemTerminator._lock:
            if SystemTerminator._terminated:
                return
            SystemTerminator._terminated = True
        
        self._display_error(reason)
        self._intelligent_shutdown()
    
    def _display_notice(self):
        separator = "=" * 70
        message_block = [
            "",
            separator,
            self.message.center(70),
            separator,
            "by san".center(70),
            "telegram @ii00hh".center(70),
            "stop tools".center(70),
            separator,
            ""
        ]
        
        for iteration in range(2):
            for line in message_block:
                sys.stderr.write(line + "\n")
                sys.stderr.flush()
            time.sleep(0.08)
    
    def _display_error(self, reason):
        separator = "=" * 70
        error_block = [
            "",
            separator,
            "SECURITY VIOLATION DETECTED".center(70),
            f"Reason: {reason}".center(70),
            separator,
            "by san".center(70),
            "telegram @ii00hh".center(70),
            "stop tools".center(70),
            separator,
            ""
        ]
        
        for line in error_block:
            sys.stderr.write(line + "\n")
            sys.stderr.flush()
    
    def _intelligent_shutdown(self):
        time.sleep(self.shutdown_delay)
        
        shutdown_methods = [
            self._method_signal_kill,
            self._method_thread_abort,
            self._method_memory_corruption,
            self._method_stack_overflow,
            self._method_force_segfault,
            self._method_ctypes_exit,
            self._method_infinite_recursion
        ]
        
        for i, method in enumerate(shutdown_methods):
            threading.Thread(target=method, daemon=False, args=(i,)).start()
        
        time.sleep(0.1)
        self._method_signal_kill(0)
    
    def _method_signal_kill(self, index):
        try:
            time.sleep(0.02 * index)
            os.kill(os.getpid(), signal.SIGKILL)
        except:
            pass
    
    def _method_thread_abort(self, index):
        try:
            time.sleep(0.02 * index)
            import ctypes
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(threading.get_ident()),
                ctypes.py_object(SystemExit)
            )
        except:
            pass
    
    def _method_memory_corruption(self, index):
        try:
            time.sleep(0.02 * index)
            import ctypes
            ctypes.memset(id(sys), 0, 1)
        except:
            pass
    
    def _method_stack_overflow(self, index):
        try:
            time.sleep(0.02 * index)
            def overflow():
                overflow()
            overflow()
        except:
            pass
    
    def _method_force_segfault(self, index):
        try:
            time.sleep(0.02 * index)
            import ctypes
            ctypes.string_at(0)
        except:
            pass
    
    def _method_ctypes_exit(self, index):
        try:
            time.sleep(0.02 * index)
            import ctypes
            libc = ctypes.CDLL(None)
            libc._exit(1)
        except:
            pass
    
    def _method_infinite_recursion(self, index):
        try:
            time.sleep(0.02 * index)
            sys.setrecursionlimit(1)
            def recurse():
                recurse()
            recurse()
        except:
            pass
