import subprocess
import sys

def pick_folder_sub() -> str | None:
    if sys.platform == "darwin":
        result = subprocess.run(
            ["osascript", "-e", "POSIX path of (choose folder)"],
            capture_output=True, text=True,
        )
        return result.stdout.strip() if result.returncode == 0 else None

    elif sys.platform == "win32":
        script = (
            "Add-Type -AssemblyName System.Windows.Forms;"
            "$d = New-Object System.Windows.Forms.FolderBrowserDialog;"
            "if ($d.ShowDialog() -eq 'OK') { $d.SelectedPath }"
        )
        result = subprocess.run(
            ["powershell", "-Command", script],
            capture_output=True, text=True,
        )
        path = result.stdout.strip()
        return path if path else None

    else:  # Linux
        for cmd in [["zenity", "--file-selection", "--directory"],
                    ["kdialog", "--getexistingdirectory"]]:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.stdout.strip() if result.returncode == 0 else None
            except FileNotFoundError:
                continue
        return None