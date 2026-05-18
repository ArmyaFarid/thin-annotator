import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from data.loader_image import init_thin_section_fov_images

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

def pick_folder_and_init_section_fov_images():
    path = pick_folder_sub()
    thin_section_id , fov_id , image_count = init_thin_section_fov_images(path)
    annotations = None
    path = Path(path)
    annotation_file = path / "annotations.json"

    if annotation_file.exists():
        try:
            with open(annotation_file, 'r', encoding='utf-8') as f:
                annotations = json.load(f)
            print(f"Loaded existing annotations from {annotation_file}")
        except Exception as e:
            print(f"Error reading existing annotations.json: {e}")
            # Keep annotations as None if file is corrupted
            annotations = None

    return {"pairsCode": thin_section_id,"image_count":image_count, "sampleId": fov_id, "annotations": annotations}