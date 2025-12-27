from datetime import datetime
from extensions import db


class ProcessingSession(db.Model):
    __tablename__ = "processing_sessions"

    id = db.Column(db.Integer, primary_key=True)

    image_id = db.Column(
        db.Integer,
        db.ForeignKey("images.id"),
        nullable=False
    )

    sharpness = db.Column(db.Float, nullable=False)
    motion_blur = db.Column(db.Float, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
