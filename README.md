# Rust Time Overlay

A lightweight always-on-top overlay for Rust that displays the current in-game server time (day/night cycle) and live player population — pulled directly from your server via the Rust+ API.

## Download

**[⬇ Download latest release](../../releases/latest)**

Unzip and run `Rust Time Overlay.exe`. No installation required.

---

## Preview

![overlay preview](icon.png)

---

## Features

- ☀️ / 🌙 Real-time day/night indicator with exact server time
- ☠ Live server population count
- Fully transparent, borderless overlay — stays on top while you play
- Drag to reposition anywhere on screen
- Scroll wheel to resize font on the fly
- Configurable font size, transparency, and text color
- All settings saved automatically between sessions
- Reconnects to your last server automatically on relaunch

---

## Requirements

- Windows 10 or 11
- [Node.js](https://nodejs.org) — only needed once during first-time setup
- The **Rust+** companion app linked to your Steam account on your phone

---

## First-time Setup

1. **Download and run** `Rust Time Overlay.exe`
2. The setup screen opens automatically and walks you through three steps:

   **Step 1 — Install Node.js**
   If Node.js is not detected, click **Install Node.js → nodejs.org**, run the installer, then click **I've installed it — Check Again**.

   **Step 2 — Link your Steam account**
   Click **Link Steam Account**. A browser page opens — sign in to Steam and close it. This only needs to be done once.

   **Step 3 — Pair with your Rust server**
   Click **Start Listening for Pair**, then in-game go to **Menu → alarm clock icon → Pair**. The overlay connects automatically.

3. Done — the overlay appears and starts showing live data. Next time you launch, it reconnects automatically with no setup required.

> Node.js is only used during the pairing process. Once paired, the overlay runs standalone.

---

## Changing Servers

Open settings (double-click the overlay or right-click → Open Settings), then click **Change Server**. This jumps straight to the pairing step — click **Start Listening for Pair** and pair again from inside Rust.

---

## Controls

| Action | Result |
|--------|--------|
| Drag overlay | Reposition it on screen |
| Scroll wheel on overlay | Resize the font |
| Double-click overlay | Open settings panel |
| Right-click overlay | Quick menu (reconnect / exit) |
| Escape in settings | Hide the settings panel |
| Hide button | Minimize to overlay only |

---

## Settings

All settings are found in the settings panel (double-click the overlay to open):

| Setting | Description |
|---------|-------------|
| Font Size | Slider — adjusts overlay text size (12–60) |
| Transparency | Slider — adjusts overlay opacity |
| Text Color | Color picker for overlay text |
| Show population | Toggle the ☠ player count row on/off |

---

## Building from Source

**Install dependencies:**
```
pip install rustplus pyinstaller
```

**Build the exe:**

Double-click `build.bat` — it detects your Python, installs dependencies, and produces `dist\Rust Time Overlay.exe` automatically.

Or manually:
```
pyinstaller "Rust Time Overlay.spec" --noconfirm
```

---

## Privacy & Config

Your server credentials (IP, port, Steam ID, auth token) are stored locally in `rust_overlay_config.json` next to the exe. This file is never uploaded anywhere and is excluded from the repository via `.gitignore`.

---

## Troubleshooting

**Overlay doesn't connect after launch**
Your server token may have expired. Click **Change Server** in settings and pair again from inside Rust.

**"rustplus library not installed" warning**
Open a terminal and run:
```
"C:\Python3xx\python.exe" -m pip install rustplus
```
Use the exact Python path shown in the warning.

**Node.js not detected after installing**
Restart your PC so PATH updates take effect, then click **I've installed it — Check Again**.
