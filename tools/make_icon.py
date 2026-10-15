"""Gera assets/icon.ico a partir de shiftlight/icon.py."""
import os
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)
from shiftlight.icon import make_icon

os.makedirs(os.path.join(root, "assets"), exist_ok=True)
make_icon(True, 256).save(os.path.join(root, "assets", "icon.ico"),
                          sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("assets/icon.ico gerado")
