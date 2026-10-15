"""Loop de telemetria -> LEDs, pensado para rodar numa thread de fundo."""
import socket
import threading
import time
from typing import Callable, Optional

from . import forza
from .leds import G29Leds
from .mapping import rpm_to_mask

NO_WHEEL = "Volante não encontrado"
PORT_BUSY = "Porta em uso"
WAITING = "Aguardando o jogo"
PLAYING = "Conectado ao jogo"

IDLE_AFTER = 1.0   # s sem pacotes -> considera o jogo parado
RETRY_EVERY = 2.0  # s entre tentativas de reabrir volante/porta


class ShiftLightEngine:
    def __init__(self, host: str = "0.0.0.0", port: int = 5300,
                 on_status: Optional[Callable[[str], None]] = None,
                 leds_factory: Callable[[], G29Leds] = G29Leds) -> None:
        self.host, self.port = host, port
        self.on_status = on_status or (lambda s: None)
        self._leds_factory = leds_factory
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.status = ""

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, name="shiftlight", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=3)

    def _set_status(self, status: str) -> None:
        if status != self.status:
            self.status = status
            self.on_status(status)

    def _run(self) -> None:
        sock = leds = None
        last_mask, last_packet = -1, 0.0
        try:
            while not self._stop.is_set():
                if leds is None:
                    try:
                        leds = self._leds_factory()
                        last_mask = -1
                    except (OSError, RuntimeError):
                        self._set_status(NO_WHEEL)
                        self._stop.wait(RETRY_EVERY)
                        continue
                if sock is None:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.bind((self.host, self.port))
                        sock.settimeout(0.5)
                    except OSError:
                        sock.close()
                        sock = None
                        self._set_status(PORT_BUSY)
                        self._stop.wait(RETRY_EVERY)
                        continue
                    self._set_status(WAITING)

                try:
                    data, _ = sock.recvfrom(1024)
                except socket.timeout:
                    if time.monotonic() - last_packet > IDLE_AFTER:
                        self._set_status(WAITING)
                        mask = 0
                    else:
                        continue
                else:
                    t = forza.parse(data)
                    if t is None:
                        continue
                    last_packet = time.monotonic()
                    self._set_status(PLAYING)
                    mask = rpm_to_mask(t.rpm, t.idle_rpm, t.max_rpm) if t.race_on else 0

                if mask != last_mask:
                    try:
                        if leds.set_mask(mask) < 0:
                            raise OSError("write falhou")
                        last_mask = mask
                    except OSError:  # volante desconectado: tenta reabrir
                        self._close_leds(leds)
                        leds = None
        finally:
            if leds is not None:
                self._close_leds(leds)
            if sock is not None:
                sock.close()

    @staticmethod
    def _close_leds(leds: G29Leds) -> None:
        try:
            leds.close()
        except OSError:
            pass
