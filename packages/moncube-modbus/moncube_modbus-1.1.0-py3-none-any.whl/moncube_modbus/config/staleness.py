"""Staleness detection configuration."""

from dataclasses import dataclass


@dataclass
class StalenessConfig:
    """Configuration for data staleness detection."""
    
    warnSec: int = 30
    """Seconds before data is considered stale (warning)."""
    
    badSec: int = 120
    """Seconds before data is considered bad (error)."""
