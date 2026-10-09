# Copyright (c) 2025 Armya BAKOUAN.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file in the root directory of this source tree.

import multiprocessing
import sys
import threading
import webbrowser
import tkinter as tk
import urllib.request
import os
import signal
import subprocess
import time
from tkinter import filedialog, messagebox, ttk

from dataset_manager.coco_extractor import build_dataset
from main import start_backend_logic

STEP_NAMES = {
    "SCANNING": "Scanning dataset",
    "JSON_FILES_COMPUTING": "Reading annotations",
    "ZIPPING": "Writing ZIP archive",
    "COPYING": "Copying uncompressed images",
    "FINALIZING": "Finalizing dataset"
}

def kill_port(port):
    try:
        if sys.platform != "win32":
            subprocess.run(f"lsof -ti:{port} | xargs kill -9", shell=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(f"for /f \"tokens=5\" %a in ('netstat -aon ^| findstr :{port}') do taskkill /f /pid %a",
                           shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

WINDOW_BG = "#ececec"
TEXT_COLOR = "#1d1d1f"
UI_FONT = ("Helvetica", 14)
DOT_COLORS = {"green": "#5ac05a", "orange": "#f5a623", "red": "#e5534b"}


def round_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    points = [
        x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1, x2, y1,
        x2, y1 + r, x2, y1 + r, x2, y2 - r, x2, y2 - r, x2, y2,
        x2 - r, y2, x2 - r, y2, x1 + r, y2, x1 + r, y2, x1, y2,
        x1, y2 - r, x1, y2 - r, x1, y1 + r, x1, y1 + r, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class RoundedButton(tk.Canvas):
    def __init__(self, master, text="", command=None, primary=False, destructive_text=None, state="normal", height=44, **kwargs):
        super().__init__(master, height=height, bg=master["bg"], highlightthickness=0, bd=0, **kwargs)
        self._text = text
        self._command = command
        self._primary = primary
        self._destructive_text = destructive_text
        self._state = state
        self._hover = False
        self.bind("<Configure>", lambda e: self._draw())
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        self.bind("<ButtonRelease-1>", self._on_click)

    def configure(self, cnf=None, **kwargs):
        if "text" in kwargs:
            self._text = kwargs.pop("text")
        if "state" in kwargs:
            self._state = kwargs.pop("state")
        if cnf or kwargs:
            super().configure(cnf, **kwargs)
        self._draw()

    config = configure

    def _set_hover(self, value):
        self._hover = value
        self._draw()

    def _on_click(self, event):
        if self._state != "disabled" and self._command:
            self._command()

    def _draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 2:
            return
        disabled = self._state == "disabled"
        if self._destructive_text is not None and self._text == self._destructive_text:
            fill = "#d93d33" if self._hover and not disabled else "#e5534b"
            outline = "#c9362d"
            fg = "#ffffff"
        elif self._primary:
            fill = "#2f74e6" if self._hover and not disabled else "#3b82f6"
            outline = "#2563eb"
            fg = "#ffffff"
        else:
            fill = "#f5f5f5" if self._hover and not disabled else "#ffffff"
            outline = "#c7c7c7"
            fg = "#a0a0a0" if disabled else TEXT_COLOR
        round_rect(self, 1, 1, w - 1, h - 1, 8, fill=fill, outline=outline)
        self.create_text(w / 2, h / 2, text=self._text, fill=fg, font=UI_FONT)


class StatusCard(tk.Canvas):
    def __init__(self, master, text="", fg="red", height=52, **kwargs):
        super().__init__(master, height=height, bg=master["bg"], highlightthickness=0, bd=0, **kwargs)
        self._text = text
        self._dot = DOT_COLORS.get(fg, fg)
        self.bind("<Configure>", lambda e: self._draw())

    def configure(self, cnf=None, **kwargs):
        if "text" in kwargs:
            self._text = kwargs.pop("text")
        if "fg" in kwargs:
            fg = kwargs.pop("fg")
            self._dot = DOT_COLORS.get(fg, fg)
        if cnf or kwargs:
            super().configure(cnf, **kwargs)
        self._draw()

    config = configure

    def _draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 2:
            return
        round_rect(self, 1, 1, w - 1, h - 1, 8, fill="#ffffff", outline="#d9d9d9")
        self.create_oval(16, h / 2 - 6, 28, h / 2 + 6, fill=self._dot, outline="")
        self.create_text(40, h / 2, text=self._text, fill=TEXT_COLOR, font=UI_FONT, anchor="w")


def main():
    multiprocessing.freeze_support()
    kill_port(7263)

    root = tk.Tk()
    root.title("ThinAnnotator Control Panel")
    root.geometry("640x340")
    root.configure(bg=WINDOW_BG)

    container = tk.Frame(root, bg=WINDOW_BG)
    container.pack(fill="both", expand=True, padx=16, pady=16)

    status_label = StatusCard(container, text="Server stopped", fg="red")
    status_label.pack(fill="x")

    # Progress dots animation label
    progress_label = tk.Label(container, text="", fg="#6e6e73", bg=WINDOW_BG, font=("Helvetica", 11))
    progress_label.pack(anchor="w")

    state = {
        "process": None,
        "check_attempts": 0,
        "dot_count": 0,
        "after_id": None,
        "server_ready": False,
    }

    MAX_WAIT_SECONDS = 180  # SAM2 can be slow — give it 3 minutes

    def animate_dots():
        if state["server_ready"]:  # ADD THIS CHECK
            return
        """Animates '...' to show the UI is alive during loading."""
        if state["process"] and state["process"].is_alive():
            state["dot_count"] = (state["dot_count"] + 1) % 4
            progress_label.config(text="Loading SAM2 models" + "." * state["dot_count"])
            state["after_id"] = root.after(500, animate_dots)

    def check_server():
        """Pings the Flask server until it responds, with timeout and crash detection."""
        state["check_attempts"] += 1

        # --- Crash detection ---
        if state["process"] and not state["process"].is_alive():
            exit_code = state["process"].exitcode
            status_label.config(text=f"Server crashed (exit {exit_code})", fg="red")
            progress_label.config(text="Check terminal logs for details.")
            start_btn.config(text="Start Server")
            state["process"] = None
            return

        # --- Timeout ---
        if state["check_attempts"] > MAX_WAIT_SECONDS:
            status_label.config(text="Timeout: Server took too long", fg="red")
            progress_label.config(text=f"Tried for {MAX_WAIT_SECONDS}s. Try restarting.")
            start_btn.config(text="Start Server")
            stop_server_logic(silent=True)
            return

        # --- Ping ---
        try:
            response = urllib.request.urlopen("http://127.0.0.1:7263/healthy", timeout=1)
            if response.getcode() == 200:
                state["server_ready"] = True
                progress_label.config(text="")
                status_label.config(text="Running on http://127.0.0.1:7263", fg="green")
                browser_btn.config(state="normal")
                return  # Success — stop polling
        except:
            pass

        # Keep polling
        state["after_id"] = root.after(1000, check_server)

    def toggle_server():
        if state["process"] is None or not state["process"].is_alive():
            state["check_attempts"] = 0
            state["dot_count"] = 0
            state["server_ready"] = False

            state["process"] = multiprocessing.Process(target=start_backend_logic)
            state["process"].daemon = True
            state["process"].start()

            status_label.config(text="Loading ThinAnnotator models...", fg="orange")
            start_btn.config(text="Stop Server")
            browser_btn.config(state="disabled")

            animate_dots()
            check_server()
        else:
            stop_server_logic()

    def stop_server_logic(silent=False):
        # Cancel any pending after() callbacks
        if state["after_id"]:
            root.after_cancel(state["after_id"])
            state["after_id"] = None

        if state["process"]:
            state["process"].terminate()
            state["process"].join(timeout=2)
            if state["process"].is_alive():
                try:
                    os.kill(state["process"].pid, signal.SIGTERM)
                except:
                    pass
            state["process"] = None

        if not silent:
            progress_label.config(text="")
            status_label.config(text="Server stopped", fg="red")
            start_btn.config(text="Start Server")
            browser_btn.config(state="disabled")

    def launch_browser():
        try:
            webbrowser.get("chrome").open("http://127.0.0.1:7263")
        except webbrowser.Error:
            # Fallback to default browser if Chrome isn't found
            webbrowser.open("http://127.0.0.1:7263")

    def on_closing():
        stop_server_logic()
        root.destroy()
        sys.exit(0)

    def open_generate_dataset_window():
        window = tk.Toplevel(root)
        window.title("Generate Thin-COCO Dataset")
        # Slightly taller to fit the checkbox comfortably
        window.geometry("600x330")
        window.resizable(False, False)

        input_var = tk.StringVar()
        output_var = tk.StringVar()

        # ---------------- INPUT ----------------
        tk.Label(window, text="Source Folder:").pack(anchor="w", padx=10, pady=(10, 0))

        input_frame = tk.Frame(window)
        input_frame.pack(fill="x", padx=10)

        input_entry = tk.Entry(input_frame, textvariable=input_var, width=50)
        input_entry.pack(side="left", expand=True, fill="x")

        def browse_input():
            folder = filedialog.askdirectory(title="Select Source Folder")
            if folder:
                input_var.set(folder)

        tk.Button(input_frame, text="Browse", command=browse_input).pack(side="left", padx=5)

        # ---------------- OUTPUT ----------------
        tk.Label(window, text="Destination Folder:").pack(anchor="w", padx=10, pady=(10, 0))

        output_frame = tk.Frame(window)
        output_frame.pack(fill="x", padx=10)

        output_entry = tk.Entry(output_frame, textvariable=output_var, width=50)
        output_entry.pack(side="left", expand=True, fill="x")

        def browse_output():
            folder = filedialog.askdirectory(title="Select Destination Folder")
            if folder:
                output_var.set(folder)

        tk.Button(output_frame, text="Browse", command=browse_output).pack(side="left", padx=5)

        # ---------------- ZIP CHECKBOX ----------------
        zip_var = tk.BooleanVar(value=False)  # Defaults to False (fast folder export)
        zip_checkbox = tk.Checkbutton(
            window,
            text="Compress as .zip archive (Slower but saves space)",
            variable=zip_var
        )
        zip_checkbox.pack(anchor="w", padx=10, pady=(10, 0))

        # ---------------- PROGRESS UI COMPONENTS ----------------
        progress_var = tk.DoubleVar(value=0)

        progress_bar = ttk.Progressbar(
            window,
            variable=progress_var,
            maximum=100,
            length=400
        )
        progress_bar.pack(pady=(15, 10))

        step_label = tk.Label(
            window,
            text="Preparing...",
            font=("Arial", 10, "bold")
        )
        step_label.pack()

        progress_label = tk.Label(window, text="Waiting...")
        progress_label.pack()

        def update_progress(current_action, current, total, filename):
            percent = (current / total) * 100
            filename = os.path.basename(str(filename))

            def ui_update():
                progress_var.set(percent)
                step_label.config(
                    text=STEP_NAMES.get(current_action, current_action)
                )
                progress_label.config(
                    text=f"{current}/{total} • {filename} • {percent:.1f}%"
                )

            window.after(0, ui_update)

        # ---------------- GENERATE LOGIC & BUTTON ----------------
        def generate_dataset():
            input_folder = input_var.get()
            output_folder = output_var.get()

            if not input_folder or not output_folder:
                messagebox.showerror("Error", "Please select both folders.")
                return

            def worker():
                try:
                    # Get checkbox state: True if checked, False if not
                    should_zip = zip_var.get()

                    # Call the updated build_dataset function
                    exported_path = build_dataset(
                        root_dir=input_folder,
                        output_dir=output_folder,
                        zip_output=should_zip,
                        progress_callback=update_progress
                    )

                    window.after(
                        0,
                        lambda: messagebox.showinfo(
                            "Success",
                            f"Thin-COCO dataset generated successfully!\n\nSaved to:\n{exported_path}"
                        )
                    )
                    window.after(0, window.destroy)

                except Exception as e:
                    window.after(
                        0,
                        lambda: messagebox.showerror(
                            "Generation Error",
                            str(e)
                        )
                    )

            threading.Thread(target=worker, daemon=True).start()

        tk.Button(
            window,
            text="Generate",
            command=generate_dataset,
            width=20,
            height=1
        ).pack(pady=10)

    start_btn = RoundedButton(container, text="Start Server", command=toggle_server, primary=True, destructive_text="Stop Server")
    start_btn.pack(fill="x", pady=(8, 0))

    browser_btn = RoundedButton(container, text="Open Annotator", command=launch_browser, state="disabled")
    browser_btn.pack(fill="x", pady=(8, 0))

    collect_dataset_btn = RoundedButton(
        container,
        text="Generate Thin-COCO dataset",
        command=open_generate_dataset_window,
    )
    collect_dataset_btn.pack(fill="x", pady=(8, 0))

    exit_btn = RoundedButton(container, text="Exit Entirely", command=on_closing)
    exit_btn.pack(fill="x", pady=(8, 0))

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()