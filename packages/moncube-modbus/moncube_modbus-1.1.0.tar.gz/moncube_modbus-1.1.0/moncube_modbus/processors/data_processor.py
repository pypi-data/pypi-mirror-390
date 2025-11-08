"""Data processor for converting MQTT data payloads to Modbus registers."""

import logging
from typing import Callable

from ..constants import (
    DATA_TEMP_START, DATA_PD_START, DATA_ARC_START, DATA_HUM_START
)
from ..utils import parse_float, parse_int, parse_iso8601_to_epoch


class DataProcessor:
    """Processes data from MQTT messages and writes to Modbus registers."""
    
    def __init__(
        self,
        write_int16: Callable[[int, int], None],
        write_uint16: Callable[[int, int], None],
        write_uint32_split: Callable[[int, int], None],
    ):
        """
        Initialize processor with register write functions.
        
        Args:
            write_int16: Function to write signed 16-bit value to register
            write_uint16: Function to write unsigned 16-bit value to register
            write_uint32_split: Function to write 32-bit value across two registers
        """
        self.write_int16 = write_int16
        self.write_uint16 = write_uint16
        self.write_uint32_split = write_uint32_split
    
    def process_temperature(self, base_addr: int, data: dict):
        """Process temperature data (scaled ×10)."""
        temp = data.get("temperature", {}) or {}
        
        def write_temp(slot: int, key: str):
            value = parse_float(temp.get(key))
            if value is not None:
                self.write_int16(base_addr + slot, round(value * 10))
        
        write_temp(0, "busbarTemp")
        write_temp(1, "ambientTemp")
        write_temp(2, "tempR")
        write_temp(3, "tempS")
        write_temp(4, "tempT")
        write_temp(5, "deltaMax")
        write_temp(6, "busbarPeak24h")
    
    def process_humidity(self, base_addr: int, data: dict):
        """Process humidity data (scaled ×10)."""
        humidity = data.get("humidity", {}) or {}
        
        value = parse_float(humidity.get("humidity"))
        if value is not None:
            self.write_int16(base_addr, round(value * 10))
        
        value_max = parse_float(humidity.get("humidityMax24h"))
        if value_max is not None:
            self.write_int16(base_addr + 1, round(value_max * 10))
    
    def process_arc(self, base_addr: int, data: dict):
        """Process arc detection data."""
        arc = data.get("arc", {}) or {}
        
        def write_arc(slot: int, key: str, scale: int = 1):
            value = parse_float(arc.get(key))
            if value is not None:
                self.write_int16(base_addr + slot, int(round(value * scale)))
        
        write_arc(0, "arcIntensityLevel")
        write_arc(1, "arcDurationMs")
        
        # Timestamp (32-bit, 2 registers)
        ts_arc = parse_iso8601_to_epoch(arc.get("arcPeakIntensity24hDate"))
        if ts_arc is not None:
            self.write_uint32_split(base_addr + 2, ts_arc)
        
        write_arc(4, "arcDetected24h")
        write_arc(5, "arcPeakIntensity24h")
        
        # Voltage and current measurements
        for slot, key in [
            (6, "voltageR"), (7, "voltageS"), (8, "voltageT"),
            (9, "currentR"), (10, "currentS"), (11, "currentT")
        ]:
            value = parse_float(arc.get(key))
            if value is not None:
                self.write_int16(base_addr + slot, int(value))
    
    def process_partial_discharge(self, base_addr: int, data: dict):
        """Process partial discharge data."""
        pd = data.get("partialDischarge", {}) or {}
        
        def write_pd(slot: int, key: str):
            value = parse_float(pd.get(key))
            if value is not None:
                self.write_int16(base_addr + slot, int(value))
        
        write_pd(0, "amplitude")
        write_pd(1, "dischargeRate")
        write_pd(2, "accuPdAlarmS")
        write_pd(3, "accuPdAlarm7dS")
        write_pd(4, "dischargeCount24h")
        write_pd(5, "dischargePeak24h")
        
        # Timestamp 1 (32-bit, 2 registers)
        ts1 = parse_iso8601_to_epoch(pd.get("dischargePeak24hDate"))
        if ts1 is not None:
            self.write_uint32_split(base_addr + 6, ts1)
        
        write_pd(8, "dischargeRatePeak24h")
        
        # Timestamp 2 (32-bit, 2 registers)
        ts2 = parse_iso8601_to_epoch(pd.get("dischargeRatePeak24hDate"))
        if ts2 is not None:
            self.write_uint32_split(base_addr + 9, ts2)
    
    def process_all_data(self, idx: int, block_size: int, cubicle_base_offset: int, data: dict):
        """
        Process all data types for a cubicle.
        
        Args:
            idx: Cubicle index
            block_size: Size of register block per cubicle
            cubicle_base_offset: Offset where cubicle data starts (after hash table)
            data: Data dictionary from MQTT payload
        """
        base = cubicle_base_offset + (idx * block_size)
        
        self.process_temperature(base + DATA_TEMP_START, data)
        self.process_humidity(base + DATA_HUM_START, data)
        self.process_arc(base + DATA_ARC_START, data)
        self.process_partial_discharge(base + DATA_PD_START, data)
