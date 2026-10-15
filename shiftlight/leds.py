"""Controle dos 5 LEDs do G29 via HID cru.

Comando (baseado no driver Linux hid-lg4ff): F8 12 <máscara> 00 00 00 00
Máscara: bit0 = LED mais à esquerda ... bit4 = mais à direita. [a confirmar no Windows]

O G29 expõe a interface 0 (joystick, usage_page 0001), cujo output report não tem
ID e carrega 16 bytes, e a interface 1 (vendor ff00, HID++). O comando vai na
interface 0; como não há report ID, o 1º byte enviado pelo hidapi deve ser 0x00.
"""
import hid

VID = 0x046D
PIDS = (0xC24F,  # G29 modo nativo (PC)
        0xC260)  # G29 modo PS4


def find_paths() -> list[bytes]:
    """Caminhos HID do G29, interface de joystick (usage_page 0001, usage 0004) primeiro."""
    infos = [d for pid in PIDS for d in hid.enumerate(VID, pid)]
    infos.sort(key=lambda d: (d["usage_page"], d["usage"]) != (0x0001, 0x0004))
    return [d["path"] for d in infos]


class G29Leds:
    def __init__(self, path: bytes | None = None, report_len: int = 17) -> None:
        paths = [path] if path else find_paths()
        if not paths:
            raise RuntimeError("G29 não encontrado (VID 046d). O G HUB/volante está conectado?")
        self.dev = hid.device()
        self.dev.open_path(paths[0])
        self.path = paths[0]
        self.report_len = report_len

    def set_mask(self, mask: int) -> int:
        # byte 0 = report ID 0 (sem ID); depois F8 12 <máscara> + zeros até 16 bytes de dados
        data = bytes([0x00, 0xF8, 0x12, mask & 0x1F]) + bytes(self.report_len - 4)
        return self.dev.write(data)

    def close(self) -> None:
        self.set_mask(0)
        self.dev.close()
