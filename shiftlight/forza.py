"""Parser mínimo do pacote UDP "Data Out" do Forza (só os campos de RPM)."""
import struct
from typing import NamedTuple, Optional

# Início do bloco "Sled" (igual em FH4/FH5/FM7): IsRaceOn, TimestampMS, MaxRpm, IdleRpm, CurrentRpm
_HEAD = struct.Struct("<iIfff")


class Telemetry(NamedTuple):
    race_on: bool
    max_rpm: float
    idle_rpm: float
    rpm: float


def parse(packet: bytes) -> Optional[Telemetry]:
    if len(packet) < _HEAD.size:
        return None
    race_on, _ts, max_rpm, idle_rpm, rpm = _HEAD.unpack_from(packet)
    return Telemetry(bool(race_on), max_rpm, idle_rpm, rpm)
