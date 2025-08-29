# Auto Bing Search

A tiny cross-platform desktop app that opens your browser and runs a series of Bing searches using a curated word list. Built with **PySide6** and a minimal, modern UI.

---

## Highlights

* **Start → 5-second countdown → search loop** (10s between searches).
* **Start / Pause / Stop** controls with state-aware buttons.
* **Pin on top** toggle with visual highlight.
* **Remaining counter** appears when the run starts.
* **Global stop hotkey** (works unfocused once permissions are granted):

  * **macOS:** `Esc` (native event tap; falls back to AppKit/pynput).
  * **Windows:** `Ctrl+Alt+S` *(use left Ctrl + left Alt)* — app registers a system hotkey and has two fallbacks.
  * **Linux:** `Esc` via `pynput`.
* **Focus recovery**: before every search the app refocuses the browser window.
* **Search box first, address bar if needed**: types into Bing’s on-page box; if that can’t be focused, it focuses the address bar and types the query like normal text.
* **Edge preference** (falls back to default browser).
* **Single file** distribution on Windows & Linux; **Universal 2** app on macOS.

---

## How it works (per OS)

* **macOS**

  * Activates your browser, focuses Bing’s search box, types human-like, and presses Return.
  * If the box can’t be focused, it hits **Cmd+L**, types the query in the address bar, and presses Return.
  * On first launch, a **one-time permissions helper** appears with buttons to open **Accessibility**, **Input Monitoring**, and **Automation** panes.

* **Windows**

  * Global stop: **Ctrl+Alt+S** (left keys recommended). Registered via `RegisterHotKey` with low-level and pynput fallbacks.
  * Types into Bing’s box; if that fails, uses **Ctrl+L** to type in the address bar and presses Enter.
  * The app attempts to bring a major browser (Edge/Chrome/Firefox/Brave/Opera) to the foreground before each search.

* **Linux**

  * Uses `pyautogui` for typing; `Esc` stops via `pynput`.
  * X11 recommended (Wayland may block automation). If available, `wmctrl`/`xdotool` help focusing the browser.
  * Falls back to **Ctrl+L** → address bar typing when the on-page box can’t be focused.

---

## Project layout

```
Auto Bing Search/
├─ auto_bing_search.py
├─ requirements.txt
├─ assets/
│  ├─ app.png
│  ├─ app.icns
│  └─ app.ico
└─ .github/workflows/    (optional)
```

The word list lives in `auto_bing_search.py` under `random_words`.

---

## Requirements

* **Python 3.12** recommended.
* Install from `requirements.txt`:

  * `PySide6`
  * `pynput`
  * `pyautogui` *(Windows/Linux)*
  * `pyobjc` *(macOS only)*
* **Linux packages** (Ubuntu example):

  ```bash
  sudo apt-get update
  sudo apt-get install -y --no-install-recommends \
    libxkbcommon-x11-0 libxcb-xinerama0 libxcb-icccm4 libxcb-image0 \
    libxcb-keysyms1 libxcb-render0 libxcb-shape0 libxcb-xfixes0 \
    libxcb-randr0 libdbus-1-3 libgl1 wmctrl xdotool
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

---

## Using the app

1. Launch the app.
2. If prompted, confirm whether you’re signed into Bing.

   * **Sign in** opens Bing’s sign-in page.
   * Check **Remember** to skip the prompt next time (Shift+Start always shows it).
3. Set a count with the stepper and click **Start**.
4. A **5-second** countdown appears; the search loop starts.
5. During the run:

   * **Pause** toggles pause/resume.
   * **Stop** ends the session.
   * **Global stop hotkeys**:

     * macOS: **Esc**
     * Windows: **Ctrl+Alt+S**
     * Linux: **Esc**
6. **Pin** keeps the window on top.

---

## Troubleshooting

* **macOS: stop hotkey not working**
  Open the app from `/Applications` and allow **Accessibility** and **Input Monitoring** (and **Automation**) in *System Settings → Privacy & Security*. The first-run helper can open those panes.

* **Windows: Ctrl+Alt+S doesn’t trigger**
  Make sure no other app uses that hotkey. Try running the host (Terminal/VS Code) as Administrator. Only one instance should register the hotkey.

* **Linux: automation not working**
  Use an **Xorg** session. Install `wmctrl` and `xdotool` for better focusing (see packages above).

* **Search goes to the URL bar**
  That’s the intended fallback when the on-page box can’t be focused; it still types the query like normal text and presses Enter. **Bing must be your browser’s default search engine for this fallback to search Bing; otherwise your default engine will be used.**

---

## Notes

* 10s delay between searches; 5s pre-run countdown.
* Browser is refocused before **every** search.
* Hold **Shift** while clicking **Start** to force the login dialog.
* Settings are stored via `QSettings` under `AutoBingSearch/App`.
