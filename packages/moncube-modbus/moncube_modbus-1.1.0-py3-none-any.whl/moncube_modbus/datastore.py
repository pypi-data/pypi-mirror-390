"""Thread-safe Modbus datastore implementation."""

import threading
from typing import List

from pymodbus.datastore import ModbusSequentialDataBlock


class ThreadSafeDataBlock(ModbusSequentialDataBlock):
    """Thread-safe wrapper for Modbus sequential data block."""
    
    def __init__(self, address: int, values: List[int]):
        super().__init__(address, values)
        self._lock = threading.RLock()
    
    def setValues(self, address, values):
        """Set register values (thread-safe)."""
        with self._lock:
            return super().setValues(address, values)
    
    def getValues(self, address, count=1):
        """Get register values (thread-safe)."""
        with self._lock:
            return super().getValues(address, count)
