# G29 Shift Light for Forza

[**⬇ Download G29ShiftLight.exe**](https://github.com/DemetrioG/logitech-g29-shift-light/releases/latest/download/G29ShiftLight.exe) · [🇧🇷 Português](#-português)

Makes the **shift-light LEDs on the Logitech G29** work in Forza Horizon (which doesn't drive them natively).
It reads the game's UDP telemetry ("Data Out") and lights the 5 LEDs as RPM climbs. Runs quietly in the Windows system tray.

## How to use

1. **Download** [`G29ShiftLight.exe`](https://github.com/DemetrioG/logitech-g29-shift-light/releases/latest/download/G29ShiftLight.exe) and run it.
   A 5-LED icon appears in the system tray (near the clock; it may be under the `^` arrow). Gray = waiting for the game, colored = connected.
   > Windows SmartScreen may warn about an unknown publisher (the app is not code-signed). Click **More info → Run anyway**.
2. **Allow the game to send telemetry (once):** right-click the tray icon → **Configurar Windows para o Forza... / Configure Windows for Forza...** → accept the administrator prompt → restart the game.
3. **In Forza:** Settings → HUD and Gameplay → **Data Out: ON**, **Data Out IP Address: `127.0.0.1`**, **Data Out IP Port: `5300`**.
4. Drive. LEDs start lighting at ~70% of the RPM range and flash near the limit.

Tray menu: status, *Start with Windows*, quit. Logitech G HUB can stay open or closed.

<details><summary>Manual setup (if the menu option fails)</summary>

PowerShell **as administrator**:

    CheckNetIsolation LoopbackExempt -a -n="Microsoft.SunriseBaseGame_8wekyb3d8bbwe"
    New-NetFirewallRule -DisplayName "G29 Shift Light UDP" -Direction Inbound -Protocol UDP -LocalPort 5300 -Action Allow
</details>

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Tray status "Volante não encontrado" (wheel not found) | G29 unplugged or not in PC mode (USB PID `046d:c24f`). Replug it. |
| Status stays "Aguardando o jogo" (waiting for game) | Data Out is off/wrong IP or port, you're in a menu (the game only sends while driving), or step 2 wasn't done — restart the game afterwards. |
| Status "Porta em uso" (port in use) | Another program listens on UDP 5300 (e.g. a dashboard app). Close it. |

## Compatibility

Tested with **G29 in PC mode** and **Forza Horizon 4** (Microsoft Store / Xbox app) on Windows. Other Logitech wheels and other Forza titles that use the same Data Out format may work but are **not verified**. The `.exe` is unsigned, so antivirus software may flag it (common with PyInstaller apps) — you can inspect the source here and build it yourself.

## How it works

- **Telemetry:** the game sends a 324-byte UDP packet (~60 Hz); current RPM, max RPM and idle RPM are the first floats after `IsRaceOn`/`TimestampMS`.
- **LEDs:** the G29 joystick HID interface accepts a 16-byte output report with no report ID: `F8 12 <5-bit mask>` (same command as the Linux `hid-lg4ff` driver). hidapi needs a leading `00` byte (report ID 0).
- Forza (UWP) can't talk to `127.0.0.1` by default, hence the loopback exemption + firewall rule from step 2.

## Build from source (Windows)

    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements-dev.txt
    python run_tray.py               # tray app
    python -m shiftlight.main        # console version
    python -m pytest tests           # tests (no hardware needed)
    .\build.ps1                      # builds dist\G29ShiftLight.exe

Diagnostic tools in `tools/`: `sniff_udp.py` (telemetry), `test_leds.py` (LEDs), `list_hid.py` / `dump_descriptors.py` (HID).
Releases: pushing a `v*` tag runs `.github/workflows/release.yml`, which builds the `.exe` on GitHub and attaches it to the Release.

*Not affiliated with Logitech, Microsoft or Playground Games. "Forza" and "Logitech" are trademarks of their respective owners. Use at your own risk.*

---

# 🇧🇷 Português

Faz os **LEDs de shift light do Logitech G29** funcionarem no Forza Horizon (que não os aciona nativamente).
Lê a telemetria UDP do jogo ("Saída de dados") e acende os 5 LEDs conforme o RPM sobe. Roda em segundo plano na bandeja do Windows.

## Como usar

1. **Baixe** o [`G29ShiftLight.exe`](https://github.com/DemetrioG/logitech-g29-shift-light/releases/latest/download/G29ShiftLight.exe) e execute.
   Um ícone de 5 LEDs aparece na bandeja (perto do relógio, talvez dentro da seta `^`). Cinza = aguardando o jogo, colorido = conectado.
   > O Windows SmartScreen pode avisar sobre editor desconhecido (o app não é assinado). Clique em **Mais informações → Executar assim mesmo**.
2. **Libere o envio de telemetria (uma vez):** botão direito no ícone → **Configurar Windows para o Forza...** → aceite o pedido de administrador → reinicie o jogo.
3. **No Forza:** Configurações → HUD e Jogabilidade → **Saída de dados: SIM**, **Endereço IP: `127.0.0.1`**, **Porta: `5300`**.
4. Dirija. Os LEDs acendem a partir de ~70% do range de RPM e piscam perto do limite.

Menu da bandeja: status, *Iniciar com o Windows* e sair. O G HUB pode ficar aberto ou fechado.

## Problemas comuns

- **"Volante não encontrado":** G29 desconectado ou fora do modo PC (`046d:c24f`). Reconecte.
- **"Aguardando o jogo" não sai:** Saída de dados desligada/IP ou porta errados, você está em menu (o jogo só envia dirigindo) ou faltou o passo 2 — reinicie o jogo depois.
- **"Porta em uso":** outro programa escuta a porta UDP 5300. Feche-o.

## Compatibilidade

Testado com **G29 em modo PC** e **Forza Horizon 4** (Microsoft Store / app Xbox). Outros volantes Logitech e outros Forza com o mesmo formato podem funcionar, mas **não foram verificados**.
