from datetime import datetime
from extensions import db


class Image(db.Model):
    __tablename__ = "images"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)

    original_filename = db.Column(db.String(255), nullable=False)

    upload_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
