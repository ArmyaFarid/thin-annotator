import shutil
from datetime import datetime
import json
import os
from pathlib import Path

from schema.annotator import AnnotatorProfile


def resolve_task_file(project_root, annotator: AnnotatorProfile | None) -> Path:
    project_root = Path(project_root)
    base_file = project_root / "task.json"

    if annotator is None:
        return base_file

    username = annotator.username
    if "/" in username or username in ("", ".", ".."):
        raise ValueError(f"invalid username: {username!r}")

    user_file = project_root / f"{username}_task.json"

    if not user_file.exists() and base_file.exists():
        shutil.copy2(base_file, user_file)
    return user_file


def get_task_snapshot(project_root, annotator: AnnotatorProfile | None):
    project_file = resolve_task_file(project_root, annotator)

    if not project_file.exists():
        return None

    with open(project_file, "r", encoding="utf-8") as f:
        saved = json.load(f)

    if isinstance(saved, list):
        return saved                    # legacy format
    if isinstance(saved, dict):
        return saved.get("data")

    raise ValueError(f"unexpected task.json structure: {type(saved).__name__}")


def save_task_snapshot(project_root, pairs_code, sample_id, annotation_data, annotator : AnnotatorProfile):
    project_root = Path(project_root)

    if annotator:
        project_file = project_root / f"{annotator.username}_task.json"
    else:
        project_file = project_root / "task.json"

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