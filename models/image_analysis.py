from datetime import datetime
from extensions import db


class ImageAnalysis(db.Model):
    __tablename__ = "image_analysis"

    id = db.Column(db.Integer, primary_key=True)

    image_id = db.Column(
        db.Integer,
        db.ForeignKey("images.id", ondelete="CASCADE"),
        nullable=False
    )

    sharpness = db.Column(db.Float, nullable=False)
    brightness = db.Column(db.Float, nullable=False)
    contrast = db.Column(db.Float, nullable=False)
    noise = db.Column(db.Float, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
