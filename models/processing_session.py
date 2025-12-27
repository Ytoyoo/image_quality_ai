from datetime import datetime
from extensions import db


class ProcessingSession(db.Model):
    __tablename__ = "processing_sessions"

    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey("images.id"), nullable=False)

    brightness_score = db.Column(db.Float)
    sharpness_score = db.Column(db.Float)
    blur_score = db.Column(db.Float)
    color_balance_score = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    result = db.relationship(
        "Result", backref="session", uselist=False, cascade="all, delete-orphan"
    )
