"""Modbus TCP server configuration."""

from dataclasses import dataclass


@dataclass
class ModbusConfig:
    """Modbus TCP server configuration."""
    
    host: str = "0.0.0.0"
    """Bind address for Modbus TCP server."""
    
    port: int = 502
    """Port for Modbus TCP server (502 is standard, requires root)."""
