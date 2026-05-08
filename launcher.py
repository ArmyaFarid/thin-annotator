import multiprocessing
import sys
import webbrowser
import tkinter as tk
import urllib.request
import os
import signal
import subprocess
import time
from main import start_backend_logic

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

def main():
    multiprocessing.freeze_support()
    kill_port(7263)

    root = tk.Tk()
    root.title("ThinAnnotator Control Panel")
    root.geometry("350x280")

    status_label = tk.Label(root, text="Server Status: Offline", fg="red", font=("Arial", 10, "bold"))
    status_label.pack(pady=10)

    # Progress dots animation label
    progress_label = tk.Label(root, text="", fg="orange", font=("Arial", 9))
    progress_label.pack()

    state = {
        "process": None,
        "check_attempts": 0,
        "dot_count": 0,
        "after_id": None,
    }

    MAX_WAIT_SECONDS = 180  # SAM2 can be slow — give it 3 minutes

    def animate_dots():
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
                progress_label.config(text="")
                status_label.config(text="Server Status: Ready (Port 7263)", fg="green")
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

            state["process"] = multiprocessing.Process(target=start_backend_logic)
            state["process"].daemon = True
            state["process"].start()

            status_label.config(text="Status: Loading SAM2 Models...", fg="orange")
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
            status_label.config(text="Server Status: Offline", fg="red")
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

    start_btn = tk.Button(root, text="Start Server", command=toggle_server, width=25, height=2)
    start_btn.pack(pady=5)

    browser_btn = tk.Button(root, text="Open Annotator", command=launch_browser, state="disabled", width=25, height=2)
    browser_btn.pack(pady=5)

    exit_btn = tk.Button(root, text="Exit Entirely", command=on_closing, width=25, height=2)
    exit_btn.pack(pady=5)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()