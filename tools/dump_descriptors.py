"""Lê (sem escrever nada) o descritor HID de cada interface do G29 e lista os relatórios de saída."""
import sys

sys.path.insert(0, __file__.rsplit("tools", 1)[0])
import hid

from shiftlight.leds import PIDS, VID


def output_reports(desc: bytes):
    """Percorre os itens do descritor e coleta (report_id, bits) de cada item Output."""
    report_id, size, count = 0, 0, 0
    bits: dict[int, int] = {}
    i = 0
    while i < len(desc):
        b = desc[i]
        if b == 0xFE:  # item longo
            i += 3 + desc[i + 1]
            continue
        n = {0: 0, 1: 1, 2: 2, 3: 4}[b & 3]
        val = int.from_bytes(desc[i + 1:i + 1 + n], "little")
        tag = b & 0xFC
        if tag == 0x84:
            report_id = val
        elif tag == 0x74:
            size = val
        elif tag == 0x94:
            count = val
        elif tag == 0x90:  # Output
            bits[report_id] = bits.get(report_id, 0) + size * count
        i += 1 + n
    return bits


for d in (x for pid in PIDS for x in hid.enumerate(VID, pid)):
    print(f"\n== interface {d['interface_number']} usage_page {d['usage_page']:04x} usage {d['usage']:04x}")
    dev = hid.device()
    try:
        dev.open_path(d["path"])
        desc = bytes(dev.get_report_descriptor())
    except (OSError, ValueError) as e:
        print("   erro:", e)
        continue
    finally:
        dev.close()
    print(f"   descritor: {len(desc)} bytes")
    outs = output_reports(desc)
    for rid, nbits in sorted(outs.items()):
        print(f"   OUTPUT report id 0x{rid:02x}: {nbits // 8} bytes de dados")
    if not outs:
        print("   (nenhum relatório de saída)")
    print("   hex:", desc.hex())
