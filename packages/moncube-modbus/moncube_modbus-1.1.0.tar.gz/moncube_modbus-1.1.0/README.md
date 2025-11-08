# Moncube Modbus Facade

Expose Moncube MQTT sensor data via Modbus TCP for integration with SCADA systems and industrial monitoring tools.

## Installation

```bash
pip install moncube-modbus
```

Or from source:

```bash
git clone https://github.com/moncube/moncube-modbus.git
cd moncube-modbus
pip install -e .
```

## Quick Start

### 1. Create Configuration File

Generate a sample configuration:

```bash
moncube-modbus init -o config.yaml
```

Or run without subcommand (backward compatible):

```bash
python -m moncube_modbus init -o config.yaml
```

Then edit `config.yaml` to add your cubicle UUIDs:

```yaml
mqtt:
  url: "broker.emqx.io"
  qos: 1
  username: ""
  password: ""

modbus:
  host: "0.0.0.0"
  port: 5020 # Use 502 for standard (requires root)

cubicles:
  "2cf51a55-a4bc-4ec2-b22c-a0054963677b": 0
  "6e9f7bf2-2f9b-4a6f-8b83-9b9c10f2a0a1": 1

staleness:
  warnSec: 30
  badSec: 120
```

### 2. Run the Server

```bash
moncube-modbus run -c config.yaml --log INFO
```

Or use the shorter form:

```bash
moncube-modbus -c config.yaml --log INFO
```

## Usage as a Library

```python
from moncube_modbus import ModbusFacade, FacadeConfig
import yaml

# Load configuration
with open("config.yaml") as f:
    config_data = yaml.safe_load(f)
config = FacadeConfig.from_dict(config_data)

# Create and run facade
facade = ModbusFacade(config)
facade.run()  # Blocks until stopped
```

## Register Layout

📖 **For detailed register documentation, see [REGISTERS.md](REGISTERS.md)**
