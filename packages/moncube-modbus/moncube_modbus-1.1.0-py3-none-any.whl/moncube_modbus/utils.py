"""Utility functions for data parsing and conversion."""

import logging
from datetime import datetime, timezone
from typing import Optional


def clamp_int16(n: int) -> int:
    """Clamp integer to signed 16-bit range."""
    return max(-32768, min(32767, int(n)))


def clamp_uint16(n: int) -> int:
    """Clamp integer to unsigned 16-bit range."""
    return max(0, min(0xFFFF, int(n)))


def parse_float(value) -> Optional[float]:
    """Safely parse a value to float."""
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def parse_int(value) -> Optional[int]:
    """Safely parse a value to integer."""
    if value is None:
        return None
    try:
        return int(float(value))
    except Exception:
        return None


def parse_iso8601_to_epoch(timestamp: str) -> Optional[int]:
    """
    Parse ISO8601 timestamp to Unix epoch seconds (UTC).
    
    Examples:
        '2025-11-04T06:19:32.4145346Z' -> epoch seconds
        '2025-11-04T06:19:32+00:00' -> epoch seconds
    """
    if not timestamp:
        return None
    
    ts = str(timestamp).strip()
    
    # Replace 'Z' with '+00:00' for parsing
    if ts.endswith('Z'):
        ts = ts[:-1] + '+00:00'
    
    # Truncate fractional seconds to 6 digits (microseconds)
    if '.' in ts:
        pre, post = ts.split('.', 1)
        tzpos_plus = post.rfind('+')
        tzpos_minus = post.rfind('-')
        tzpos = max(tzpos_plus, tzpos_minus)
        
        if tzpos > 0:
            frac = post[:tzpos]
            tz = post[tzpos:]
        else:
            frac = post
            tz = ''
        
        if len(frac) > 6:
            frac = frac[:6]
        
        ts = f"{pre}.{frac}{tz}"
    
    try:
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    except Exception:
        try:
            dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S%z")
            return int(dt.timestamp())
        except Exception:
            logging.warning("Failed to parse ISO8601 timestamp: %s", timestamp)
            return None
