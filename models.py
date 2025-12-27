from datetime import datetime
from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    images = db.relationship(
        "Image", backref="user", cascade="all, delete-orphan"
    )


class Image(db.Model):
    __tablename__ = "images"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    sessions = db.relationship(
        "ProcessingSession", backref="image", cascade="all, delete-orphan"
    )


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


class Result(db.Model):
    __tablename__ = "results"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(
        db.Integer,
        db.ForeignKey("processing_sessions.id"),
        unique=True,
        nullable=False
    )
    processed_filename = db.Column(db.String(255), nullable=False)
    quality_score = db.Column(db.Float)
    verdict = db.Column(db.Text)
