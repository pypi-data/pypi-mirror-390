"""Main Modbus facade implementation."""

import json
import logging
import threading
import time
from typing import Dict, Optional

from paho.mqtt import client as mqtt
from pymodbus import ModbusDeviceIdentification
from pymodbus.datastore import ModbusServerContext, ModbusDeviceContext
from pymodbus.server import StartTcpServer, ServerStop

from .config import FacadeConfig
from .constants import (
    ALARM_REGION_START, ALARM_REGION_SIZE, BLOCK_SIZE,
    META_AGE_OFFSET, META_QUALITY_OFFSET,
    QUALITY_GOOD, QUALITY_STALE, QUALITY_BAD
)
from .datastore import ThreadSafeDataBlock
from .processors import DataProcessor, AlarmProcessor
from .utils import clamp_int16, clamp_uint16


class ModbusFacade:
    """
    Moncube Modbus TCP facade.
    
    Exposes Moncube sensor data from MQTT as Modbus TCP holding registers.
    """
    
    def __init__(self, config: FacadeConfig):
        """
        Initialize the facade.
        
        Args:
            config: Complete facade configuration
        """
        self.config = config
        self.stop_evt = threading.Event()
        
        # Calculate total register space needed
        # Layout: [Cubicle 0: 0-999] [Cubicle 1: 1000-1999] [Cubicle 2: 2000-2999] ...
        # No shared hash table needed anymore (direct slot mapping)
        max_idx = max(config.cubicles.values()) if config.cubicles else 0
        num_cubicles = max_idx + 1
        
        cubicle_data_start = 1
        
        # Each cubicle gets BLOCK_SIZE registers
        total_regs = cubicle_data_start + (num_cubicles * BLOCK_SIZE) - 1
        
        # Store for later use
        self._cubicle_base_offset = cubicle_data_start
        
        # Create thread-safe register block
        self._block = ThreadSafeDataBlock(0, [0] * total_regs)
        self._lock = self._block._lock
        
        # Create Modbus server context
        self._context = ModbusServerContext(
            devices=ModbusDeviceContext(di=None, co=None, hr=self._block, ir=None),
            single=True
        )
        
        # Initialize processors
        self._data_processor = DataProcessor(
            write_int16=self._write_int16,
            write_uint16=self._write_uint16,
            write_uint32_split=self._write_uint32_split,
        )
        
        self._alarm_processor = AlarmProcessor(
            write_uint16=self._write_uint16,    
            alarm_region_start=ALARM_REGION_START,
            alarm_region_size=ALARM_REGION_SIZE,
        )
        
        # Staleness tracking
        self._last_update_s: Dict[int, int] = {}
        
        # MQTT client (created during start)
        self._mqtt: Optional[mqtt.Client] = None
    
    def _write_uint16(self, addr: int, value: int):
        """Write unsigned 16-bit value to register."""
        self._block.setValues(addr, [clamp_uint16(value)])
    
    def _write_int16(self, addr: int, value: int):
        """Write signed 16-bit value to register."""
        v = clamp_int16(value) & 0xFFFF
        self._block.setValues(addr, [v])
    
    def _write_uint32_split(self, addr_hi: int, epoch_s: Optional[int]):
        """Write 32-bit timestamp across two registers (high word first)."""
        if epoch_s is None:
            self._block.setValues(addr_hi, [0, 0])
            return
        
        n = int(epoch_s) & 0xFFFFFFFF
        hi = (n >> 16) & 0xFFFF
        lo = n & 0xFFFF
        self._block.setValues(addr_hi, [hi, lo])
    
    def _addr_meta_age(self, idx: int) -> int:
        """Get address for age metadata register."""
        return self._cubicle_base_offset + (idx * BLOCK_SIZE) + META_AGE_OFFSET
    
    def _addr_meta_quality(self, idx: int) -> int:
        """Get address for quality metadata register."""
        return self._cubicle_base_offset + (idx * BLOCK_SIZE) + META_QUALITY_OFFSET
    
    def _process_state_message(self, cubicle_id: str, payload: dict):
        """Process a state message from MQTT."""
        idx = self.config.cubicles.get(cubicle_id)
        if idx is None:
            logging.warning("Cubicle ID %s not found in config", cubicle_id)
            return
        
        pid = payload.get("cubicleId")
        if isinstance(pid, str) and pid != cubicle_id:
            logging.warning(
                "Topic cubicleId %s != payload cubicleId %s (using topic)",
                cubicle_id, pid
            )
        
        logging.debug(
            "Processing message for cubicle %s (idx=%d), has alarms: %s, has data: %s",
            cubicle_id, idx, "alarms" in payload, "data" in payload
        )
        
        with self._lock:
            # Process alarms and data
            self._alarm_processor.process_alarms(
                idx,
                BLOCK_SIZE,
                self._cubicle_base_offset,
                payload.get("alarms") or {}
            )
            
            self._data_processor.process_all_data(
                idx,
                BLOCK_SIZE,
                self._cubicle_base_offset,
                payload.get("data") or {}
            )
            
            # Update metadata
            self._write_uint16(self._addr_meta_age(idx), 0)
            self._write_uint16(self._addr_meta_quality(idx), QUALITY_GOOD)
            self._last_update_s[idx] = int(time.time())
            
            logging.debug("Updated registers for cubicle %s at index %d", cubicle_id, idx)
    
    def _ticker(self, stop_evt: threading.Event):
        """Background thread to update age and quality metadata."""
        warn = self.config.staleness.warnSec
        bad = self.config.staleness.badSec
        
        while not stop_evt.is_set():
            now = int(time.time())
            with self._lock:
                for idx in self.config.cubicles.values():
                    last = self._last_update_s.get(idx, 0)
                    age = now - last if last > 0 else 0xFFFF
                    age = clamp_uint16(age)
                    self._write_uint16(self._addr_meta_age(idx), age)
                    
                    # Determine quality based on age
                    if age == 0xFFFF:
                        quality = QUALITY_BAD
                    elif age <= warn:
                        quality = QUALITY_GOOD
                    elif age <= bad:
                        quality = QUALITY_STALE
                    else:
                        quality = QUALITY_BAD
                    
                    self._write_uint16(self._addr_meta_quality(idx), quality)
            
            stop_evt.wait(1.0)
    
    def _start_mqtt(self, stop_evt: threading.Event):
        """Start MQTT client and subscribe to topics."""
        url = self.config.mqtt.url
        
        # Handle URL with or without protocol
        if url.startswith("mqtt://") or url.startswith("tcp://"):
            hostport = url.split("://", 1)[1]
        else:
            hostport = url
        
        if ":" in hostport:
            host, port_s = hostport.split(":", 1)
            try:
                port = int(port_s)
            except Exception:
                port = 1883
        else:
            host, port = hostport, 1883
        
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        if self.config.mqtt.username:
            client.username_pw_set(
                self.config.mqtt.username,
                self.config.mqtt.password or ""
            )
        
        def on_connect(cl, userdata, flags, rc, properties):
            if rc != 0:
                logging.error("MQTT connect failed rc=%s", rc)
                return
            
            logging.info("MQTT connected")
            
            # Subscribe to each configured cubicle ID
            for cub_id in self.config.cubicles.keys():
                topic = f"moncube/cubicle/+/+/+/{cub_id}"
                cl.subscribe(topic, qos=self.config.mqtt.qos)
                logging.info("Subscribed to %s", topic)
        
        def on_message(cl, userdata, msg):
            try:
                logging.debug("MQTT message received on topic: %s", msg.topic)
                parts = msg.topic.split("/")
                
                # Topic format: moncube/cubicle/{org}/{site}/{area}/{cubicle}
                # OR: moncube/cubicle/{org}/{site}/{area}/{cubicle}/state
                if len(parts) < 6:
                    logging.debug("Topic too short, ignoring. Parts: %s", parts)
                    return
                
                # Extract cubicle ID (last part or second-to-last if ends with /state)
                if parts[-1] == "state":
                    cubicle_id = parts[-2]
                else:
                    cubicle_id = parts[-1]
                
                logging.debug("Extracted cubicle_id: %s", cubicle_id)
                
                if cubicle_id not in self.config.cubicles:
                    logging.debug(
                        "Cubicle ID not in config, ignoring. Known IDs: %s",
                        list(self.config.cubicles.keys())
                    )
                    return
                
                payload = json.loads(msg.payload.decode("utf-8"))
                logging.debug("Payload parsed successfully for cubicle %s", cubicle_id)
                
                if not isinstance(payload, dict):
                    logging.warning("Payload is not a dict: %s", type(payload))
                    return
                
                logging.info("Processing state message for cubicle %s", cubicle_id)
                self._process_state_message(cubicle_id, payload)
                
            except Exception as e:
                logging.exception("MQTT message error: %s", e)
        
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(host, port, keepalive=60)
        client.loop_start()
        self._mqtt = client
        
        # Wait for stop event
        while not stop_evt.is_set():
            stop_evt.wait(0.2)
        
        try:
            client.loop_stop()
            client.disconnect()
        except Exception:
            pass
    
    def _start_modbus_server(self, stop_evt: threading.Event):
        """Start Modbus TCP server."""
        identity = ModbusDeviceIdentification(
            info_name={
                "VendorName": "Moncube",
                "ProductCode": "MONCUBE",
                "VendorUrl": "https://moncube.local",
                "ProductName": "Moncube Modbus Facade",
                "ModelName": "HR-Only",
                "MajorMinorRevision": "1.0.0",
            }
        )
        
        def run_server():
            StartTcpServer(
                context=self._context,
                identity=identity,
                address=(self.config.modbus.host, self.config.modbus.port),
            )
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for stop event or KeyboardInterrupt
        try:
            while not stop_evt.is_set():
                stop_evt.wait(0.5)
        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt in server loop")
            stop_evt.set()
    
    def run(self):
        """
        Run the facade (blocking).
        
        Starts all background threads and the Modbus server.
        """
        logging.info("Starting Moncube Modbus Facade")
        
        # Start background threads
        tick_thread = threading.Thread(
            target=self._ticker,
            args=(self.stop_evt,),
            daemon=True
        )
        tick_thread.start()
        
        mqtt_thread = threading.Thread(
            target=self._start_mqtt,
            args=(self.stop_evt,),
            daemon=True
        )
        mqtt_thread.start()
        
        try:
            # Start Modbus server (blocks)
            self._start_modbus_server(self.stop_evt)
        finally:
            self.stop_evt.set()
            logging.info("Facade stopped")
    
    def stop(self):
        """Stop the facade."""
        logging.info("Stopping facade...")
        self.stop_evt.set()
        try:
            ServerStop()
        except Exception as e:
            logging.debug("ServerStop exception (expected): %s", e)
