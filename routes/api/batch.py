from pathlib import Path

from flask import Blueprint, jsonify, request

from core.annotator import current_annotator
from core.batch import init_batch, shuffle_batch
from core.task_manager import get_task_snapshot, save_task_snapshot, load_task_from_folder
from extensions import db
from models import FOVAsset, Batch, Task
from schema.annotator import AnnotatorProfile
from schema.batch import BatchSummarySchema, batches_schema
from system.pickers import pick_folder_sub

from flask import request, jsonify
from sqlalchemy import func


def _payload(task, batch, annotator : AnnotatorProfile):
    data = load_task_from_folder(task.images_folder, annotator)
    has_prev = db.session.query(
        Task.query.filter(Task.batch_id == batch.id, Task.order < task.order).exists()
    ).scalar()
    has_next = db.session.query(
        Task.query.filter(Task.batch_id == batch.id, Task.order > task.order).exists()
    ).scalar()
    return {
        "taskId": task.id,
        "pairsCode": data["pairsCode"],
        "sampleId": data["sampleId"],
        "imageCount": data["image_count"],
        "annotations": data["annotations"],
        "index": task.order,
        "total": batch.task_count,
        "isAnnotated": task.is_annotated,
        "hasPrev": has_prev,
        "hasNext": has_next,
    }


def _set_current(batch_id, task):
    Task.query.filter_by(batch_id=batch_id, is_current=True).update(
        {"is_current": False}, synchronize_session="fetch"
    )
    db.session.flush()                      # required, or the partial index rejects the next write
    if task is not None:
        task.is_current = True


def _complete(task):
    if task.is_annotated:
        return                              # idempotent — revisits never renumber
    highest = db.session.query(
        func.coalesce(func.max(Task.annotated_order), 0)
    ).filter(Task.batch_id == task.batch_id).scalar()
    task.is_annotated = True
    task.annotated_order = highest + 1


def _frontier(batch_id):
    return (Task.query
            .filter_by(batch_id=batch_id, is_annotated=False)
            .order_by(Task.order)
            .first())

batch_blueprint = Blueprint('batch', __name__)

@batch_blueprint.route("/api/batch", methods=["GET"])
def get_batches():
    batches = Batch.query.order_by(Batch.name).all()
    return jsonify(batches_schema.dump(batches))

@batch_blueprint.route("/api/batch/create", methods=["POST"])
def open_batch_from_folder():
    path = pick_folder_sub()
    try:
        batch = init_batch("New batch", path)
        shuffle_batch(batch.id)
    except NotADirectoryError:
        return jsonify({"error": f"Not a directory: {path}"}), 400
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(BatchSummarySchema().dump(batch)), 201


@batch_blueprint.route("/api/batch/current", methods=["POST"])
def current_task():
    batch_id = (request.get_json() or {}).get("batchId")
    batch = Batch.query.get_or_404(batch_id)

    task = Task.query.filter_by(batch_id=batch_id, is_current=True).first()
    if task is None:
        task = _frontier(batch_id)
        if task is None:
            return jsonify({"done": True, "total": batch.task_count})
        _set_current(batch_id, task)
        db.session.commit()

    return jsonify(_payload(task, batch,current_annotator))

@batch_blueprint.route("/api/batch/next", methods=["POST"])
def next_task():
    batch_id = (request.get_json() or {}).get("batchId")
    batch = Batch.query.get_or_404(batch_id)
    current = Task.query.filter_by(batch_id=batch_id, is_current=True).first()

    if current is None:
        target = _frontier(batch_id)
    elif not current.is_annotated:
        _complete(current)                  # forward work: finish, jump to frontier
        target = _frontier(batch_id)
    else:
        target = (Task.query                # review mode: pure navigation
                  .filter(Task.batch_id == batch_id, Task.order > current.order)
                  .order_by(Task.order)
                  .first()) or _frontier(batch_id)

    if target is None:
        _set_current(batch_id, None)
        db.session.commit()
        return jsonify({"done": True, "total": batch.task_count})

    _set_current(batch_id, target)
    db.session.commit()
    return jsonify(_payload(target, batch,current_annotator))


@batch_blueprint.route("/api/batch/prev", methods=["POST"])
def prev_task():
    batch_id = (request.get_json() or {}).get("batchId")
    batch = Batch.query.get_or_404(batch_id)
    current = Task.query.filter_by(batch_id=batch_id, is_current=True).first()
    if current is None:
        return jsonify({"error": "no current task"}), 400

    target = (Task.query
              .filter(Task.batch_id == batch_id, Task.order < current.order)
              .order_by(Task.order.desc())
              .first())
    if target is None:
        return jsonify(_payload(current, batch,current_annotator))    # already at the start

    _set_current(batch_id, target)
    db.session.commit()
    return jsonify(_payload(target, batch,current_annotator))
