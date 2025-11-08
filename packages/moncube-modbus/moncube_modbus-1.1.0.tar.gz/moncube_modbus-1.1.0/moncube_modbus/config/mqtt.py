"""MQTT broker configuration."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class MqttConfig:
    """MQTT broker configuration."""
    
    url: str
    """MQTT broker URL (e.g., 'mqtt://broker:1883' or just 'broker.emqx.io')."""
    
    qos: int = 1
    """MQTT Quality of Service level (0, 1, or 2)."""
    
    username: Optional[str] = None
    """MQTT username (optional)."""
    
    password: Optional[str] = None
    """MQTT password (optional)."""
