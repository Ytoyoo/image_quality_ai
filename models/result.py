from datetime import datetime
from extensions import db

class Result(db.Model):
    __tablename__ = "results"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(
        db.Integer,
        db.ForeignKey("processing_sessions.id"),
        nullable=False  # ← убираем unique=True
    )
    processed_filename = db.Column(db.String(255), nullable=False)
    quality_score = db.Column(db.Float)
    verdict = db.Column(db.Text)