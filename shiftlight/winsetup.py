"""Configuração única do Windows para o Forza (UWP) enviar telemetria ao app.

Libera o loopback dos pacotes Forza/Horizon e cria a regra de firewall UDP.
Precisa de administrador: dispara o PowerShell elevado (UAC) e espera o resultado.
O script vai em texto puro no -Command (sem base64 e sem arquivo temporário, que seria
substituível por outro processo antes da elevação).
"""
import ctypes
from ctypes import wintypes

RULE_NAME = "G29 Shift Light UDP"
FH4_FAMILY = "Microsoft.SunriseBaseGame_8wekyb3d8bbwe"

OK, CANCELLED, FAILED = "ok", "cancelled", "failed"

_SEE_MASK_NOCLOSEPROCESS = 0x40
_ERROR_CANCELLED = 1223
_INFINITE = 0xFFFFFFFF


def build_script(port: int) -> str:
    """Script PowerShell em texto puro, uma linha, sem aspas duplas (vai direto no -Command)."""
    return (
        "$ErrorActionPreference = 'Stop'; "
        "try { "
        f"$families = @('{FH4_FAMILY}'); "
        "$families += Get-AppxPackage | Where-Object { $_.Name -match 'Sunrise|Forza|Horizon' } "
        "| ForEach-Object { $_.PackageFamilyName }; "
        "foreach ($f in ($families | Select-Object -Unique)) "
        "{ CheckNetIsolation LoopbackExempt -a ('-n=' + $f) | Out-Null }; "
        f"Remove-NetFirewallRule -DisplayName '{RULE_NAME}' -ErrorAction SilentlyContinue; "
        f"New-NetFirewallRule -DisplayName '{RULE_NAME}' -Direction Inbound -Protocol UDP "
        f"-LocalPort {int(port)} -Action Allow | Out-Null; "
        "exit 0 "
        "} catch { exit 1 }"
    )


class _ShellExecuteInfo(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD), ("fMask", ctypes.c_ulong), ("hwnd", wintypes.HWND),
        ("lpVerb", wintypes.LPCWSTR), ("lpFile", wintypes.LPCWSTR),
        ("lpParameters", wintypes.LPCWSTR), ("lpDirectory", wintypes.LPCWSTR),
        ("nShow", ctypes.c_int), ("hInstApp", wintypes.HINSTANCE), ("lpIDList", ctypes.c_void_p),
        ("lpClass", wintypes.LPCWSTR), ("hkeyClass", wintypes.HKEY), ("dwHotKey", wintypes.DWORD),
        ("hIconOrMonitor", wintypes.HANDLE), ("hProcess", wintypes.HANDLE),
    ]


def configure_windows(port: int = 5300) -> str:
    """Executa a configuração elevada. Retorna OK, CANCELLED (usuário negou o UAC) ou FAILED."""
    shell32, kernel32 = ctypes.windll.shell32, ctypes.windll.kernel32
    info = _ShellExecuteInfo()
    info.cbSize = ctypes.sizeof(info)
    info.fMask = _SEE_MASK_NOCLOSEPROCESS
    info.lpVerb = "runas"
    info.lpFile = "powershell.exe"
    info.lpParameters = f'-NoProfile -NonInteractive -WindowStyle Hidden -Command "{build_script(port)}"'
    info.nShow = 0  # SW_HIDE
    if not shell32.ShellExecuteExW(ctypes.byref(info)):
        return CANCELLED if kernel32.GetLastError() == _ERROR_CANCELLED else FAILED
    kernel32.WaitForSingleObject(info.hProcess, _INFINITE)
    code = wintypes.DWORD()
    kernel32.GetExitCodeProcess(info.hProcess, ctypes.byref(code))
    kernel32.CloseHandle(info.hProcess)
    return OK if code.value == 0 else FAILED
