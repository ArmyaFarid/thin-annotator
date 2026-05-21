from datetime import datetime
import json
import os
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


def save_project_data(project_root,pairs_code,sample_id,annotation_data):
    project_file = Path(project_root) / "project.json"

    payload = {
        "data": annotation_data,  # your list stays untouched
        "_meta": {
            "version": "1.0.0",
            "saved_at": datetime.utcnow().isoformat(),
            "pairs_code": pairs_code,
            "sample_id": sample_id,
        }
    }

    tmp_path = project_file.with_suffix(".tmp")
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=4)
    os.replace(tmp_path, project_file)  # atomic rename
    print(f"Annotations saved successfully for {pairs_code}/{sample_id} at {project_file}")