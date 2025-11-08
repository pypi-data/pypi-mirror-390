"""Main facade configuration."""

from dataclasses import dataclass
from typing import Dict

from .modbus import ModbusConfig
from .mqtt import MqttConfig
from .staleness import StalenessConfig


@dataclass
class FacadeConfig:
    """Complete configuration for Moncube Modbus facade."""
    
    mqtt: MqttConfig
    """MQTT broker configuration."""
    
    modbus: ModbusConfig
    """Modbus TCP server configuration."""
    
    cubicles: Dict[str, int]
    """Mapping of cubicle IDs to their index in the register space."""
    
    staleness: StalenessConfig
    """Data staleness detection configuration."""
    
    @classmethod
    def from_dict(cls, data: dict) -> "FacadeConfig":
        """Create configuration from dictionary (typically loaded from YAML)."""
        mqtt_cfg = MqttConfig(**data.get("mqtt", {}))
        modbus_cfg = ModbusConfig(**data.get("modbus", {}))
        staleness_cfg = StalenessConfig(**data.get("staleness", {}))
        cubicles = {str(k): int(v) for k, v in (data.get("cubicles", {}) or {}).items()}
        
        return cls(
            mqtt=mqtt_cfg,
            modbus=modbus_cfg,
            cubicles=cubicles,
            staleness=staleness_cfg,
        )
