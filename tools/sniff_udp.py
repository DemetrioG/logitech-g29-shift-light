"""Passo 1: imprime RPM recebido do Forza para validar o Data Out e os offsets."""
import socket
import sys

sys.path.insert(0, __file__.rsplit("tools", 1)[0])
from shiftlight import forza

port = int(sys.argv[1]) if len(sys.argv) > 1 else 5300
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0", port))
print(f"Escutando UDP :{port}")
while True:
    data, addr = s.recvfrom(2048)
    t = forza.parse(data)
    print(f"{len(data)} bytes de {addr[0]} | {t}")
