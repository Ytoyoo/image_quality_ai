import os

class Config:
    SECRET_KEY = "1234"

    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg2://postgres:1234@localhost:5432/image_quality_ai_DB"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
