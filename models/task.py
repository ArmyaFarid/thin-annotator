import uuid

from sqlalchemy import CheckConstraint, Index, UniqueConstraint
from extensions import db


class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    batch_id = db.Column(
        db.String(36),
        db.ForeignKey("batch.id", ondelete="CASCADE"),
        nullable=False,
    )

    images_folder = db.Column(db.String(255), nullable=False)

    is_annotated = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())

    is_current = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())

    annotated_order = db.Column(db.Integer, nullable=True)

    order = db.Column("order", db.Integer, nullable=True)

    batch = db.relationship("Batch", back_populates="tasks")

    __table_args__ = (
        UniqueConstraint("batch_id", "images_folder", name="uq_task_batch_folder"),
        UniqueConstraint("batch_id", "order", name="uq_task_batch_order"),
        UniqueConstraint("batch_id", "annotated_order", name="uq_task_batch_annotated_order"),
        CheckConstraint('"order" IS NULL OR "order" >= 1', name="ck_task_order_min"),
        CheckConstraint("annotated_order IS NULL OR annotated_order >= 1", name="ck_task_annotated_order_min"),
        # One current task per batch. Partial index: only rows with is_current = true
        # participate, so unlimited non-current rows are fine.
        Index(
            "uq_task_one_current_per_batch",
            "batch_id",
            unique=True,
            sqlite_where=db.text("is_current"),
            postgresql_where=db.text("is_current"),
        ),
    )