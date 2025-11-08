"""Register layout constants for Moncube Modbus facade."""

# Per-cubicle block size
# Cubicle 0: 0-999, Cubicle 1: 1000-1999, Cubicle 2: 2000-2999, etc.
BLOCK_SIZE = 1000

# Alarm region (direct slot-to-status mapping) - per cubicle
# Slots are 1-indexed in MQTT (1-100), 0-indexed internally (0-99)
ALARM_REGION_START = 0  # Relative to cubicle base
ALARM_REGION_SIZE = 100  # 100 alarm slots

# Meta region - per cubicle
META_REGION_START = ALARM_REGION_START + ALARM_REGION_SIZE  # 100
META_AGE_OFFSET = META_REGION_START + 0  # 100
META_QUALITY_OFFSET = META_REGION_START + 1  # 101
NEXT_AFTER_META = META_REGION_START + 16  # 116 - leave small headroom

# Data regions (fixed, 16 registers each)
DATA_REGION_SIZE = 16
DATA_TEMP_START = NEXT_AFTER_META  # 116
DATA_PD_START = DATA_TEMP_START + DATA_REGION_SIZE  # 132
DATA_ARC_START = DATA_PD_START + DATA_REGION_SIZE  # 148
DATA_HUM_START = DATA_ARC_START + DATA_REGION_SIZE  # 164

# Alarm severity domain
SEVERITY_MIN = 1  # Good
SEVERITY_MAX = 4  # Critical
# 1=Good, 2=Warning, 3=Alert, 4=Critical

# Data quality values
QUALITY_GOOD = 0
QUALITY_STALE = 1
QUALITY_BAD = 2
