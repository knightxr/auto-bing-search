# Auto Bing Search

A tiny cross-platform desktop app that opens your browser and runs a series of Bing searches using a curated word list. Built with **PySide6** and a minimal, modern UI.

---

## Highlights

* **Start → 5-second countdown → search loop** (10s between searches).
* **Start / Pause / Stop** controls with state-aware buttons.
* **Pin on top** toggle with visual highlight.
* **Remaining counter** appears when the run starts.
* **Global `Esc` to stop**, even when the app isn’t focused:

  * macOS: native AppKit monitor (preferred), falls back to `pynput`.
  * Windows/Linux: `pynput`.
* **Login prompt** on first run (or when forced with **Shift+Start**):

  * “I’m logged in” or “Sign in”.
  * **Remember** checkbox in the dialog and a compact checkbox in the title bar.
* **Human-like typing** and tab/address-bar focus.
* **Edge preference** (falls back to default browser).
* **Single file** distribution on Windows & Linux; **Universal 2** app on macOS.

---

## How it works (per OS)

* **macOS**
  Uses AppleScript / System Events to activate the browser, focus the address bar, type, and press Return.
  Needs **Accessibility** and **Input Monitoring** permissions (System Settings → Privacy & Security).

* **Windows & Linux**
  Uses `pyautogui` for keyboard automation. On Linux, X11 is recommended (Wayland can block global hotkeys and automation).

---

## Project layout

```
Auto Bing Search/
├─ auto_bing_search.py        # main app
├─ requirements.txt           # runtime deps
├─ assets/
│  ├─ app.png                 # source icon (1024x1024)
│  ├─ app.icns                # mac app icon
│  └─ app.ico                 # windows icon (multi-size)
└─ .github/workflows/         # optional: CI build actions (if you added them)
```

> The word list is embedded in `auto_bing_search.py` under `random_words` (single-spaced entries).

---

## Requirements

* **Python 3.12** recommended.
* **Deps:** installed from `requirements.txt`:

  * `PySide6`
  * `pynput`
  * `pyobjc` *(macOS only, installed automatically via `pip` when on mac)*
  * `pyautogui` *(Windows/Linux only)*
* On **Linux**, install system libs for Qt apps (Ubuntu example):

  ```bash
  sudo apt-get update
  sudo apt-get install -y --no-install-recommends \
    libxkbcommon-x11-0 libxcb-xinerama0 libxcb-icccm4 libxcb-image0 \
    libxcb-keysyms1 libxcb-render0 libxcb-shape0 libxcb-xfixes0 \
    libxcb-randr0 libdbus-1-3 libgl1
  ```

---

## Setup (dev)

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python auto_bing_search.py
```

### Windows (PowerShell)

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python auto_bing_search.py
```

> Do **not** commit the `.venv/` folder; use `requirements.txt`.

---

## Using the app

1. Launch the app.
2. If prompted, confirm whether you’re signed into Bing.

   * **Sign in** opens the Bing sign-in page.
   * Check **Remember** to skip the prompt next time (Shift+Start always shows it).
3. Adjust the count with the **– / +** stepper.
4. Click **Start** → a **5-second** pre-run countdown shows.
5. During the run:

   * **Pause** toggles pause/resume.
   * **Stop** ends the session.
   * **Esc** stops immediately (works unfocused once permissions are granted).
6. **Pin** keeps the window always on top (button highlights when active).

---

## Troubleshooting

* **Esc doesn’t stop when unfocused (macOS)**
  Open the bundled app from `/Applications` and grant:

  * *System Settings → Privacy & Security → Accessibility*
  * *Input Monitoring*
    If you run from Terminal/VS Code, grant those hosts too.

* **Linux automation not working**
  Use an **Xorg** session (Wayland may block automation). Ensure the listed Qt/X11 libs are installed.

* **Edge not opening**
  The app prefers Edge if found, otherwise falls back to the default browser.

---

## Notes

* The interval between searches is **10 seconds**.
* Pre-run countdown is **5 seconds**.
* Hold **Shift** while clicking **Start** to always show the login dialog.
* Settings are stored via `QSettings` under `AutoBingSearch/App`.
