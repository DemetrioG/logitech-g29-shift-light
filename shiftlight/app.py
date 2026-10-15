"""App de bandeja do Windows: roda o shift light em segundo plano."""
import argparse
import ctypes
import os
import sys
import threading

import pystray

from .engine import PLAYING, ShiftLightEngine
from .icon import make_icon
from .winsetup import CANCELLED, OK, configure_windows

APP_NAME = "G29ShiftLight"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _autostart_command() -> str:
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "run_tray.py")
    return f'"{pythonw}" "{script}"'


def autostart_enabled() -> bool:
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            return winreg.QueryValueEx(key, APP_NAME)[0] == _autostart_command()
    except OSError:
        return False


def set_autostart(enabled: bool) -> None:
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _autostart_command())
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass


def _already_running() -> bool:
    """Mutex nomeado: impede duas instâncias disputando a porta UDP."""
    kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW(None, False, f"Local\\{APP_NAME}")
    return kernel32.GetLastError() == 183  # ERROR_ALREADY_EXISTS


def main() -> None:
    ap = argparse.ArgumentParser(description="G29 Shift Light (bandeja)")
    ap.add_argument("--port", type=int, default=5300)
    args = ap.parse_args()

    if _already_running():
        return

    icon = pystray.Icon(APP_NAME, make_icon(False), f"{APP_NAME}")

    def on_status(status: str) -> None:
        icon.icon = make_icon(status == PLAYING)
        icon.title = f"G29 Shift Light — {status}"
        icon.update_menu()

    engine = ShiftLightEngine(port=args.port, on_status=on_status)

    def toggle_autostart(icon_, item) -> None:
        set_autostart(not autostart_enabled())

    def configure(icon_, item) -> None:
        def work() -> None:
            result = configure_windows(args.port)
            icon.notify({
                OK: "Pronto! Reinicie o Forza para a telemetria funcionar.",
                CANCELLED: "Configuração cancelada (permissão de administrador negada).",
            }.get(result, "Não foi possível configurar o Windows. Veja o README para o passo manual."),
                "G29 Shift Light")
        threading.Thread(target=work, daemon=True).start()

    def quit_app(icon_, item) -> None:
        engine.stop()
        icon_.stop()

    icon.menu = pystray.Menu(
        pystray.MenuItem(lambda item: f"Status: {engine.status or 'iniciando...'}", None, enabled=False),
        pystray.MenuItem(f"Porta UDP: {args.port}", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Configurar Windows para o Forza...", configure),
        pystray.MenuItem("Iniciar com o Windows", toggle_autostart, checked=lambda item: autostart_enabled()),
        pystray.MenuItem("Sair", quit_app),
    )
    engine.start()
    icon.run()


if __name__ == "__main__":
    main()
