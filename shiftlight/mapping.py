"""RPM -> máscara de 5 LEDs (progressivo, pisca no limite)."""
import time

# Fração do range de RPM em que cada LED acende
THRESHOLDS = (0.70, 0.78, 0.86, 0.92, 0.97)
FLASH_AT = 0.985
FLASH_HZ = 8


def rpm_to_mask(rpm: float, idle: float, max_rpm: float) -> int:
    if max_rpm <= idle:
        return 0
    pct = (rpm - idle) / (max_rpm - idle)
    if pct >= FLASH_AT:
        return 0x1F if int(time.monotonic() * FLASH_HZ * 2) % 2 == 0 else 0
    mask = 0
    for i, t in enumerate(THRESHOLDS):
        if pct >= t:
            mask |= 1 << i
    return mask
