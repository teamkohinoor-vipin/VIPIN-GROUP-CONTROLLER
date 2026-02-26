import re
from config import TIME_UNITS

def parse_time(time_str: str) -> int:
    """Convert time string like 1h, 2d to seconds."""
    match = re.match(r'^(\d+)([mhdw])$', time_str)
    if not match:
        return 0
    value, unit = match.groups()
    return int(value) * TIME_UNITS[unit]
