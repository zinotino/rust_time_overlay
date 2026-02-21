import tkinter as tk
from tkinter import ttk, colorchooser
import json
import os
import re
import asyncio
import threading
import subprocess
import pathlib
import sys

# ─────────────────────────────────────────────
# Safe rustplus import (prevents silent crash)
# ─────────────────────────────────────────────

try:
    from rustplus import RustSocket, ServerDetails
except Exception as e:
    print("ERROR: rustplus not installed.")
    print("Run: pip install rustplus")
    print("Details:", e)
    input("Press Enter to exit...")
    raise


__version__ = "3.1.0"

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────

CONFIG_FILE = str(pathlib.Path(__file__).parent / "rust_overlay_config.json")

DEFAULT_CONFIG = {
    "ip": "",
    "port": 28082,
    "steamid": 0,
    "token": 0,
    "x": 10,
    "y": 10,
    "font_size": 14,
    "alpha": 0.92,
    "color": "#d0d0d0"
}


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_CONFIG.copy()


def save_config():
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


config = load_config()

# ─────────────────────────────────────────────
# Rust State
# ─────────────────────────────────────────────

rust_connected = False
rust_time_str = "--:--"
rust_is_day = True
rust_error = None
_stop_event = threading.Event()


def is_configured():
    return bool(config["ip"] and config["steamid"] and config["token"])


# ─────────────────────────────────────────────
# Rust Polling
# ─────────────────────────────────────────────

async def rust_loop():
    global rust_connected, rust_time_str, rust_is_day, rust_error

    while not _stop_event.is_set():
        if not is_configured():
            await asyncio.sleep(3)
            continue

        try:
            details = ServerDetails(
                config["ip"],
                config["port"],
                config["steamid"],
                config["token"]
            )

            socket = RustSocket(details)
            await socket.connect()

            rust_connected = True
            rust_error = None

            while not _stop_event.is_set():
                try:
                    info = await socket.get_time()
                    raw = info.time
                    rust_time_str = f"{int(raw)%24:02d}:{int((raw%1)*60):02d}"
                    rust_is_day = 8.0 <= raw < 20.0
                except Exception as e:
                    rust_error = str(e)
                    break

                await asyncio.sleep(10)

            rust_connected = False
            try:
                await socket.disconnect()
            except:
                pass

        except Exception as e:
            rust_error = str(e)
            rust_connected = False

        await asyncio.sleep(10)


def start_connection():
    _stop_event.clear()

    def runner():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(rust_loop())

    threading.Thread(target=runner, daemon=True).start()


def restart_connection():
    _stop_event.set()
    threading.Timer(1, start_connection).start()


# ─────────────────────────────────────────────
# Overlay Window
# ─────────────────────────────────────────────

root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", config["alpha"])
root.configure(bg="black")
root.attributes("-transparentcolor", "black")
root.geometry(f"+{config['x']}+{config['y']}")

frame = tk.Frame(root, bg="black")
frame.pack(padx=6, pady=3)

display_label = tk.Label(
    frame,
    text="☀ --:--",
    font=("Segoe UI", config["font_size"]),
    fg=config["color"],
    bg="black"
)
display_label.pack()


def update_overlay():
    if not is_configured():
        display_label.config(text="⚙ setup", fg="#666666")
    elif not rust_connected:
        display_label.config(text=f"· {rust_time_str}", fg="#555555")
    else:
        icon = "☀" if rust_is_day else "☽"
        display_label.config(text=f"{icon} {rust_time_str}",
                             fg=config["color"])

    root.after(500, update_overlay)


update_overlay()


# Dragging
def drag_start(e):
    root._x = e.x
    root._y = e.y


def drag_motion(e):
    config["x"] = root.winfo_x() - root._x + e.x
    config["y"] = root.winfo_y() - root._y + e.y
    root.geometry(f"+{config['x']}+{config['y']}")
    save_config()


display_label.bind("<Button-1>", drag_start)
display_label.bind("<B1-Motion>", drag_motion)


# Scroll resize
def resize(e):
    config["font_size"] += 1 if e.delta > 0 else -1
    config["font_size"] = max(10, min(40, config["font_size"]))
    display_label.config(font=("Segoe UI", config["font_size"]))
    save_config()


display_label.bind("<MouseWheel>", resize)


# ─────────────────────────────────────────────
# Smart Pairing
# ─────────────────────────────────────────────

def check_node():
    try:
        subprocess.check_output("node --version",
                                shell=True,
                                stderr=subprocess.DEVNULL)
        return True
    except:
        return False


def run_hidden(cmd):
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=flags
    )


def smart_connect(status_callback):

    if not check_node():
        status_callback("Node.js not installed.")
        return

    def flow():

        status_callback("Registering with Steam...")
        run_hidden(
            "npx @liamcottle/rustplus.js fcm-register"
        ).wait()

        status_callback("Listening for pairing...")

        process = run_hidden(
            "npx @liamcottle/rustplus.js fcm-listen"
        )

        body_re = re.compile(
            r"key:\s*'body',\s*value:\s*`({[^`]+})`",
            re.DOTALL
        )

        full = ""

        for line in process.stdout:
            full += line
            match = body_re.search(full)

            if match:
                try:
                    body = json.loads(match.group(1))
                    config["ip"] = body["ip"]
                    config["port"] = int(body["port"])
                    config["steamid"] = int(body["playerId"])
                    config["token"] = int(body["playerToken"])
                    save_config()
                    process.terminate()

                    status_callback("Paired successfully.")
                    restart_connection()
                    return
                except:
                    pass

        status_callback("Pairing failed.")

    threading.Thread(target=flow, daemon=True).start()


# ─────────────────────────────────────────────
# Settings Window (Rust Themed)
# ─────────────────────────────────────────────

def open_settings():
    win = tk.Toplevel(root)
    win.title("Rust Time Overlay")
    win.geometry("400x420")
    win.resizable(False, False)
    win.configure(bg="#1b1b1b")

    title = tk.Label(win,
                     text="RUST TIME OVERLAY",
                     fg="#c97c2c",
                     bg="#1b1b1b",
                     font=("Segoe UI", 14, "bold"))
    title.pack(pady=15)

    status_label = tk.Label(win,
                            text="",
                            fg="#cccccc",
                            bg="#1b1b1b",
                            font=("Segoe UI", 9))
    status_label.pack(pady=5)

    def set_status(msg):
        status_label.config(text=msg)

    ttk.Button(win,
               text="Connect to Server",
               command=lambda: smart_connect(set_status)
               ).pack(pady=10, fill="x", padx=40)

    ttk.Separator(win).pack(fill="x", pady=15, padx=20)

    tk.Label(win,
             text="Display Settings",
             fg="#c97c2c",
             bg="#1b1b1b",
             font=("Segoe UI", 11, "bold")
             ).pack(pady=10)

    size_var = tk.IntVar(value=config["font_size"])

    tk.Scale(win,
             from_=10,
             to=40,
             orient="horizontal",
             variable=size_var,
             bg="#1b1b1b",
             fg="#cccccc",
             troughcolor="#2a2a2a",
             highlightthickness=0
             ).pack(fill="x", padx=40)

    def apply_display():
        config["font_size"] = size_var.get()
        display_label.config(font=("Segoe UI",
                                   config["font_size"]))
        save_config()

    ttk.Button(win,
               text="Apply Display Changes",
               command=apply_display
               ).pack(pady=5, fill="x", padx=40)

    tk.Label(win,
             text=f"Version {__version__}",
             fg="#555555",
             bg="#1b1b1b",
             font=("Segoe UI", 8)
             ).pack(side="bottom", pady=10)


# Right click menu
def show_menu(e):
    menu = tk.Menu(root,
                   tearoff=0,
                   bg="#1b1b1b",
                   fg="#cccccc",
                   activebackground="#c97c2c",
                   activeforeground="black")
    menu.add_command(label="Settings",
                     command=open_settings)
    menu.add_separator()
    menu.add_command(label="Quit",
                     command=root.destroy)
    menu.tk_popup(e.x_root, e.y_root)


display_label.bind("<Button-3>", show_menu)


# ─────────────────────────────────────────────
# Launch
# ─────────────────────────────────────────────

if is_configured():
    start_connection()

root.mainloop()
