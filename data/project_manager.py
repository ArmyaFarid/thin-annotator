import json
from pathlib import Path


def get_project_data(project_root):
    project_file = Path(project_root) / "project.json"
    data = None
    if project_file.exists():
        with open(project_file, 'r', encoding='utf-8') as f:
            saved = json.load(f)

        if isinstance(saved, list):
            data = saved  # legacy file
        else:
            data = saved.get("data")  # new format

    return data