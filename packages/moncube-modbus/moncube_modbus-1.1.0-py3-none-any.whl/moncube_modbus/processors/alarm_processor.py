"""Alarm processor for handling direct slot-to-status mapping."""

import logging
from typing import Callable

from ..constants import SEVERITY_MIN, SEVERITY_MAX
from ..utils import parse_int


class AlarmProcessor:
    """Processes alarm data with direct slot-to-status mapping."""
    
    def __init__(
        self,
        write_uint16: Callable[[int, int], None],
        alarm_region_start: int,
        alarm_region_size: int,
    ):
        """
        Initialize alarm processor.
        
        Args:
            write_uint16: Function to write unsigned 16-bit value to register
            alarm_region_start: Start address of alarm region (relative to cubicle base)
            alarm_region_size: Total number of alarm slots (100)
        """
        self.write_uint16 = write_uint16
        self.alarm_region_start = alarm_region_start
        self.alarm_region_size = alarm_region_size
    
    def process_alarms(self, idx: int, block_size: int, cubicle_base_offset: int, alarms: dict):
        """
        Process alarm data for a cubicle with direct slot-to-status mapping.
        
        Args:
            idx: Cubicle index
            block_size: Size of register block per cubicle
            cubicle_base_offset: Offset where cubicle data starts
            alarms: Alarms dictionary from MQTT payload
                    Format: {slot_number: status}
                    Example: {1: 1, 2: 3, 3: 1}
                    slot_number: 1-indexed slot (1-100)
                    status: alarm severity (0-4)
        """
        if not isinstance(alarms, dict):
            logging.debug("Alarms is not a dict, skipping")
            return
        
        base = cubicle_base_offset + (idx * block_size)
        
        # Clear all alarm slots first (set to 0)
        for slot_idx in range(self.alarm_region_size):
            addr = base + self.alarm_region_start + slot_idx
            self.write_uint16(addr, 0)
        
        # Process each alarm slot
        for slot_key, status_raw in alarms.items():
            # Parse slot number (expecting 1-indexed from MQTT)
            slot_num = parse_int(slot_key)
            if slot_num is None:
                logging.warning("Invalid alarm slot key (not a number): %r", slot_key)
                continue
            
            # Convert from 1-indexed to 0-indexed
            slot_idx = slot_num - 1
            
            # Validate slot range (0-99 internally, 1-100 from MQTT)
            if slot_idx < 0 or slot_idx >= self.alarm_region_size:
                logging.warning(
                    "Alarm slot %d out of range (valid: 1-%d), ignoring",
                    slot_num, self.alarm_region_size
                )
                continue
            
            # Parse and validate status
            status = parse_int(status_raw)
            if status is None:
                logging.warning(
                    "Non-numeric status for slot %d: %r",
                    slot_num, status_raw
                )
                continue
            
            # Clamp status to valid range (0-4)
            status = max(SEVERITY_MIN, min(SEVERITY_MAX, status))
            
            # Calculate register address
            addr = base + self.alarm_region_start + slot_idx
            
            # Write status to register
            self.write_uint16(addr, status)
            
            logging.debug(
                "Alarm slot %d (register %d) = %d",
                slot_num, addr, status
            )

