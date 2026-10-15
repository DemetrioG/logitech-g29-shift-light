"""Tenta acender os LEDs em cada interface HID e tamanho de pacote, mostrando o retorno do write.
Observe o volante: quando acender, anote qual combinação funcionou."""
import sys
import time

sys.path.insert(0, __file__.rsplit("tools", 1)[0])
import hid

from shiftlight.leds import PIDS, VID

infos = [d for pid in PIDS for d in hid.enumerate(VID, pid)]
# uso: probe_leds.py [joystick]  -> só a interface de joystick (usage_page 0001)
if "joystick" in sys.argv[1:]:
    infos = [d for d in infos if d["usage_page"] == 0x0001 and d["usage"] == 0x0004]
for d in infos:
    print(f"\n== interface {d['interface_number']} usage_page {d['usage_page']:04x} usage {d['usage']:04x}")
    print(f"   {d['path']}")
    dev = hid.device()
    try:
        dev.open_path(d["path"])
    except OSError as e:
        print("   não abriu:", e)
        continue
    for length in (17,):
        data = bytes([0x00, 0xF8, 0x12, 0x1F]) + bytes(length - 4)
        try:
            r = dev.write(data)
        except OSError as e:
            r = f"erro {e}"
        print(f"   len={length:2d} -> write={r} {dev.error() if r == -1 else ''}")
        time.sleep(2.0)
        dev.write(bytes([0x00, 0xF8, 0x12, 0x00]) + bytes(length - 4))
        time.sleep(0.3)
    dev.close()
