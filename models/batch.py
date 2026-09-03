import uuid

from extensions import db

class Batch(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    name = db.Column(db.String(255), nullable=False)

    root_path = db.Column(db.String(255), nullable=False)

    task_count = db.Column(db.Integer, default=0)

    tasks = db.relationship(
        "Task",
        back_populates="batch",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Task.order",
    )

