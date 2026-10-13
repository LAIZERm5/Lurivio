<p align="center"><img src="docs/assets/brand.png" width="880" alt="Lurivio — select, copy, paste" /></p>
<p align="center"><strong>URLs and QR codes from your screen — on your clipboard.</strong><br />Windows · Local OCR + QR · Russian / English · Five themes</p>
<p align="center"><a href="README.md">Русский</a> · <a href="#quick-start">Quick start</a> · <a href="#qr-codes">QR codes</a></p>

![Lurivio](docs/assets/aurora.png)

## Select. Copy. Paste.

Stop retyping a URL shown in a video, image or presentation. Press a shortcut,
drag over the URL or QR code, then paste the result using **Ctrl+V** or **Paste**.
Recognition runs locally; no camera, uploads or account are required.

> **0.6.1 · Beta / release candidate.** Previously named ScreenLink.
> Local tests run on Linux / Qt offscreen. Actual Windows capture, global shortcuts,
> tray, focus restoration, startup and DPI still require Windows testing.
> Source archives do not include a built Windows EXE.

## Features

- URL text OCR, including visible bare domains.
- Single and multiple QR codes: URLs, UTF-8 text, Wi-Fi and multiline content.
- Auto, URLs-only and QR-only modes.
- Prewarmed OCR, fast single-line path and one exact-repeat in-memory cache.
- Click-to-record keyboard or modifier+mouse shortcuts, with no text typing. Keyboard shortcut conflict handling.
- Tray, notifications and opt-in Windows sign-in startup.
- Live Russian/English interface with saved language preference.
- Five themes and native Windows top-right window controls.

## Quick start

### Portable Windows build

If Releases contains a verified `Lurivio-Windows.zip`, extract **all** files
and run `Lurivio/Lurivio.exe`. Keep `_internal` beside the EXE.
Builds are unsigned; do not disable Windows security to run them.

### Source

Target: **Windows 10/11 x64, Python 3.11 x64, Python launcher**.
Download and extract the source ZIP, then run **Start.bat**.
Internet is needed to install dependencies, not for recognition.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Use **Diagnose.bat** for startup errors. Select **Settings → Interface language → English**.

## QR codes

**0.6.1 fix:** ZXing-C++ is the primary decoder, with OpenCV as fallback. Original
pixels are checked before resizing; quiet-zone padding, inversion and rounded-module
fallbacks improve difficult-code handling. This does not guarantee recovery of lost pixels.


Choose **Auto** or **QR codes only**, press **Ctrl+Shift+L** (or your shortcut),
and select the complete QR code with its light quiet-zone border.
A single valid HTTP/HTTPS URL is copied automatically when auto-copy is enabled.
Multiple results require selection and manual copying. Text, Wi-Fi, contact data and
non-web schemes always require review and **Copy**; nothing is opened or executed.

![QR result](docs/assets/qr.png)

Auto gives decoded QR payloads priority. If no QR is decoded, URL OCR runs.
Visible text beside a decoded QR is not merged into the same result.
Very thin selections skip QR scanning in Auto. URLs-only avoids QR overhead;
QR-only bypasses OCR for the selection, though OCR still warms up at app startup.

Supported: text QR codes decoded as UTF-8, not arbitrary binary data or other barcodes.
Tiny, cropped or damaged codes may not decode. Review destinations and data before
opening or pasting them, especially into a terminal.

## Preferences and background behavior

![Click-to-record shortcut](docs/assets/recorder.png)

![Settings](docs/assets/settings.png)

- Language and recognition mode apply immediately and persist.
- Click the shortcut field, press your combination, then Apply. Esc cancels recording.
- Mouse: Ctrl / Alt / Shift / Win + middle click (`MouseMiddle`) or side button (`MouseX1` / `MouseX2`) inside the recording window. Left/right clicks, scrolling and unmodified mouse buttons are not assignable.
- Single left-click on the tray icon starts capture. Right-click → Open Lurivio opens the interface; notification clicks open results.
- Shortcut changes do not need a restart; occupied new combinations preserve the old shortcut.
- Ctrl+C/X/V and F12 are excluded. Reset restores Ctrl+Shift+L if available.
- Minimize uses the taskbar. Close-to-tray is enabled by default.
- Full exit: tray icon → **Quit**. Windows startup is opt-in and hidden in the tray.
- Esc / right-click cancels selection without changing the clipboard.
- The app never injects Ctrl+V, submits a search or opens a URL.

## Upgrade 

Disable startup in the old app and fully quit it through the tray first.
Extract Lurivio; an existing `.venv` can be kept when replacing source files.
Start.bat refreshes dependencies. If no Lurivio settings exist, only old ScreenLink
preferences are read on launch. The old settings are retained; logs and results
are not imported. Re-enable startup in Lurivio if wanted; legacy startup entries
are not automatically removed.

Preferences: `%LOCALAPPDATA%\Lurivio\settings.json`.

## Privacy and limitations

Screenshots and result history are not saved or uploaded. The current result and
one repeat cache stay in memory; Clear removes them but leaves the clipboard unchanged.
Windows clipboard history/cloud sync follows Windows settings. Preferences and a
technical errors.log stay local. Mouse bindings use a Windows mouse hook; no movement or click history is saved. Unlike keyboard hotkeys, mouse bindings are not exclusively reserved and another application/driver may intercept them. OCR can misread characters and URL case.
Protected video/secure desktops may not be captured. Selection stays on the monitor
under the cursor. Screenshots illustrate the unchanged 0.6.0 interface; 0.6.1 updates the QR engine. They show the client area, not the OS-drawn native caption.

![Theme gallery](docs/assets/gallery.png)

Independent Qt themes; not affiliated with Apple or Nami. macOS names describe visual styles only.

## Development and releases

```powershell
$env:LURIVIO_TEST_OCR = "1"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Build locally with **Build_EXE.bat** after installation and quitting the app.
Windows CI tests and builds a portable archive with checksums. Pushing **v0.6.1**
creates a **draft prerelease**, not an automatically public stable release.
Verify the artifact on Windows before publishing.

[Publishing guide (RU)](docs/PUBLISHING_RU.md) · [Release checklist (RU)](docs/RELEASE_CHECKLIST_RU.md) ·
[Testing (RU)](docs/TESTING_RU.md) · [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md)

## License

Own code: [MIT](LICENSE). Dependencies and OCR models retain separate licenses;
see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Available license texts are
collected into builds; legal completeness is not guaranteed. Lurivio is the chosen
project brand, not a claim of trademark or domain registration.

[QR troubleshooting / диагностика (RU)](docs/QR_TROUBLESHOOTING_RU.md)
