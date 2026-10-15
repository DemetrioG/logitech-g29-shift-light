"""Passo 2: acende os LEDs um a um para validar o comando HID."""
import sys
import time

sys.path.insert(0, __file__.rsplit("tools", 1)[0])
from shiftlight.leds import G29Leds

leds = G29Leds()
print("G29 aberto:", leds.path)
for i in range(5):
    print(f"LED {i + 1} -> write={leds.set_mask(1 << i)}")
    time.sleep(0.6)
for m in (0x01, 0x03, 0x07, 0x0F, 0x1F, 0x00):
    print(f"máscara {m:05b} -> write={leds.set_mask(m)}")
    time.sleep(0.6)
leds.close()
