from app import app
from extensions import db
from models import Image

with app.app_context():
    image = Image(
        original_filename="test.jpg",
        user_id = "1"
    )

    db.session.add(image)
    db.session.commit()

    print("Image saved with id:", image.id)
