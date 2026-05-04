import multiprocessing
import sys
import webbrowser
import tkinter as tk
import urllib.request
import os
import signal
import subprocess
from app_for_launcher import start_backend_logic

def kill_port(port):
    """Forcefully releases the port before starting the app."""
    try:
        if sys.platform != "win32":
            # Mac/Linux command
            subprocess.run(f"lsof -ti:{port} | xargs kill -9", shell=True, 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            # Windows command
            subprocess.run(f"for /f \"tokens=5\" %a in ('netstat -aon ^| findstr :{port}') do taskkill /f /pid %a", 
                           shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

def main():
    multiprocessing.freeze_support()
    
    # Pre-launch cleanup
    kill_port(7263)
    
    root = tk.Tk()
    root.title("GeoSAM Control Panel")
    root.geometry("350x280")

    status_label = tk.Label(root, text="Server Status: Offline", fg="red", font=("Arial", 10, "bold"))
    status_label.pack(pady=20)

    # Use a dictionary to keep a mutable reference to the process
    state = {"process": None}

    def check_server():
        """Pings the Flask server until it responds."""
        try:
            response = urllib.request.urlopen("http://127.0.0.1:7263/healthy", timeout=1)
            if response.getcode() == 200:
                status_label.config(text="Server Status: Ready (Port 7263)", fg="green")
                browser_btn.config(state="normal")
                return 
        except:
            pass
        
        if state["process"] and state["process"].is_alive():
            root.after(1000, check_server)

    def toggle_server():
        if state["process"] is None or not state["process"].is_alive():
            # START SERVER
            state["process"] = multiprocessing.Process(target=start_backend_logic)
            state["process"].daemon = True
            state["process"].start()
            
            status_label.config(text="Status: Loading SAM 2 Models...", fg="orange")
            start_btn.config(text="Stop Server")
            check_server()
        else:
            # STOP SERVER
            stop_server_logic()

    def stop_server_logic():
        if state["process"]:
            # Standard terminate
            state["process"].terminate()
            state["process"].join(timeout=2)
            
            # Aggressive kill if still alive (to free VRAM)
            if state["process"].is_alive():
                try:
                    os.kill(state["process"].pid, signal.SIGTERM)
                except:
                    pass
            
            state["process"] = None
            status_label.config(text="Server Status: Offline", fg="red")
            start_btn.config(text="Start Server")
            browser_btn.config(state="disabled")

    def launch_browser():
        webbrowser.open("http://127.0.0.1:7263")

    def on_closing():
        """Cleanup everything when the X button is clicked."""
        stop_server_logic()
        root.destroy()
        sys.exit(0)

    # UI Buttons
    start_btn = tk.Button(root, text="Start Server", command=toggle_server, width=25, height=2)
    start_btn.pack(pady=5)

    browser_btn = tk.Button(root, text="Open Web App", command=launch_browser, state="disabled", width=25, height=2)
    browser_btn.pack(pady=5)

    exit_btn = tk.Button(root, text="Exit Entirely", command=on_closing, width=25, height=2)
    exit_btn.pack(pady=5)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()