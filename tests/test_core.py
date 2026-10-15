import socket
import struct
import time

from shiftlight import forza
from shiftlight.engine import NO_WHEEL, PLAYING, WAITING, ShiftLightEngine
from shiftlight.mapping import rpm_to_mask


def packet(race_on=1, max_rpm=8000.0, idle=1000.0, rpm=1000.0) -> bytes:
    return struct.pack("<iIfff", race_on, 0, max_rpm, idle, rpm) + bytes(324 - 20)


def test_parse():
    t = forza.parse(packet(rpm=6500.0))
    assert t.race_on and t.max_rpm == 8000.0 and t.idle_rpm == 1000.0 and t.rpm == 6500.0
    assert forza.parse(b"abc") is None


def test_mask_progression():
    m = lambda rpm: rpm_to_mask(rpm, 1000, 8000)
    assert m(1000) == 0
    assert m(6000) == 0b00001   # 71%
    assert m(7000) == 0b00011   # 85,7%
    assert m(7100) == 0b00111   # 87,1%
    assert m(7800) == 0b11111   # 97%, ainda sem piscar
    assert m(0) == 0


class FakeLeds:
    def __init__(self):
        self.masks = []
        self.closed = False

    def set_mask(self, mask):
        self.masks.append(mask)
        return 17

    def close(self):
        self.closed = True


def wait_for(cond, timeout=3.0):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if cond():
            return True
        time.sleep(0.02)
    return False


def test_engine_end_to_end():
    fake = FakeLeds()
    statuses = []
    eng = ShiftLightEngine("127.0.0.1", 5399, statuses.append, leds_factory=lambda: fake)
    eng.start()
    try:
        assert wait_for(lambda: WAITING in statuses)
        tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tx.sendto(packet(rpm=7200.0), ("127.0.0.1", 5399))
        assert wait_for(lambda: PLAYING in statuses)
        assert wait_for(lambda: fake.masks and fake.masks[-1] == 0b00111)
        # jogo para de enviar -> LEDs apagam e volta a aguardar
        assert wait_for(lambda: fake.masks[-1] == 0 and statuses[-1] == WAITING, timeout=4)
    finally:
        eng.stop()
    assert fake.closed


def test_engine_wheel_missing_then_found():
    fake = FakeLeds()
    calls = {"n": 0}

    def factory():
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("sem volante")
        return fake

    statuses = []
    eng = ShiftLightEngine("127.0.0.1", 5398, statuses.append, leds_factory=factory)
    eng.start()
    try:
        assert wait_for(lambda: NO_WHEEL in statuses)
        assert wait_for(lambda: WAITING in statuses, timeout=5)
    finally:
        eng.stop()


def test_winsetup_script():
    from shiftlight.winsetup import build_script
    script = build_script(5300)
    assert "-LocalPort 5300" in script and "SunriseBaseGame" in script
    assert '"' not in script and "\n" not in script  # cabe entre aspas duplas no -Command
