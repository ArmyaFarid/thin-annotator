from pathlib import Path

from numpy.distutils.fcompiler import none

from core.thin_section_fov_folder_scanner import find_fov_folders
from extensions import db
from models import Batch, Task

import random

def shuffle_batch(batch_id: str) -> None:
    tasks = Task.query.filter_by(batch_id=batch_id).all()
    positions = list(range(1, len(tasks) + 1))
    random.shuffle(positions)

    for t in tasks:              # park out of range first
        t.order = None
    db.session.flush()

    for t, pos in zip(tasks, positions):
        t.order = pos
    db.session.commit()

def init_batch(name: str, root_path: str | Path, *, commit: bool = True) -> Batch:
    """
    Scan `root_path` for FOV folders and create a Batch with one Task each.

    Tasks are ordered 1..N by the scanner's sorted folder order. The first task
    is marked current. Raises NotADirectoryError if root_path is not a directory,
    ValueError if no FOV folders are found.
    """
    root = Path(root_path).resolve()

    folders = find_fov_folders(root)          # raises NotADirectoryError
    if not folders:
        raise ValueError(f"No FOV folders found under {root}")

    batch = Batch(name=name, root_path=str(root), task_count=len(folders))
    db.session.add(batch)

    for position, folder in enumerate(folders, start=1):
        batch.tasks.append(Task(images_folder=str(folder)))

    if commit:
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
    return batch