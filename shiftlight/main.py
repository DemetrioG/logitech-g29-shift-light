"""Versão de linha de comando (com console)."""
import argparse
import time

from .engine import ShiftLightEngine


def main() -> None:
    ap = argparse.ArgumentParser(description="Shift light do G29 para Forza")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=5300)
    args = ap.parse_args()

    engine = ShiftLightEngine(args.host, args.port, on_status=lambda s: print(f"[status] {s}"))
    engine.start()
    print(f"Escutando UDP em {args.host}:{args.port} ... (Ctrl+C para sair)")
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        engine.stop()


if __name__ == "__main__":
    main()
