"""Command-line interface for Moncube Modbus Facade."""

import argparse
import logging
import signal
import sys
from pathlib import Path

import yaml

from .config import FacadeConfig
from .facade import ModbusFacade


SAMPLE_CONFIG = """# Moncube Modbus Facade Configuration

mqtt:
  url: "broker.emqx.io"
  qos: 1
  username: ""
  password: ""

modbus:
  host: "0.0.0.0"
  port: 5020  # Use 502 for standard Modbus (requires root), or 5020+ for non-privileged

cubicles:
  # Map cubicle UUIDs to register block indices
  # Example:
  # "uuid-1": 0  # Registers 0-511
  # "uuid-2": 1  # Registers 512-1023
  # "uuid-3": 2  # Registers 1024-1535

staleness:
  warnSec: 30   # Seconds before data is considered stale (warning)
  badSec: 120   # Seconds before data is considered bad (error)
"""


def create_config(output_path: str):
    """Create a sample configuration file."""
    path = Path(output_path)
    
    if path.exists():
        response = input(f"File {output_path} already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
    
    try:
        path.write_text(SAMPLE_CONFIG)
        print(f"✓ Sample configuration created at: {output_path}")
        print("\nNext steps:")
        print("1. Edit the configuration file to add your cubicle UUIDs")
        print("2. Run the server: moncube-modbus -c config.yaml")
    except Exception as e:
        print(f"✗ Failed to create configuration: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Moncube Modbus TCP Facade - Expose MQTT sensor data via Modbus"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command (default)
    run_parser = subparsers.add_parser('run', help='Run the Modbus server (default)')
    run_parser.add_argument(
        "-c", "--config",
        required=True,
        help="Path to YAML configuration file"
    )
    run_parser.add_argument(
        "--log",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)"
    )
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Create a sample configuration file')
    init_parser.add_argument(
        "-o", "--output",
        default="config.yaml",
        help="Output path for configuration file (default: config.yaml)"
    )
    
    # For backward compatibility, also accept top-level arguments
    parser.add_argument(
        "-c", "--config",
        help="Path to YAML configuration file"
    )
    parser.add_argument(
        "--log",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Handle init command
    if args.command == 'init':
        create_config(args.output)
        return
    
    # Handle run command or backward compatibility mode
    if args.command == 'run' or (args.config and not args.command):
        config_path = args.config
        log_level = args.log
    else:
        parser.print_help()
        sys.exit(1)
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s %(levelname)s %(message)s"
    )
    
    # Load configuration
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        config = FacadeConfig.from_dict(config_data)
    except Exception as e:
        logging.error("Failed to load configuration: %s", e)
        sys.exit(1)
    
    # Create and start facade
    facade = ModbusFacade(config)
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        logging.info("Shutting down...")
        facade.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        facade.run()
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt received")
        facade.stop()


if __name__ == "__main__":
    main()
