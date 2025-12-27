import os
from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

from extensions import db
from models import Image
from models import User
from config import Config

main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("image")

        if not file or file.filename == "":
            return "Файл не выбран", 400

        # ВАЖНО: для простоты пока используем одного пользователя
        user = User.query.first()
        if not user:
            user = User(email="demo@user.com")
            db.session.add(user)
            db.session.commit()

        filename = secure_filename(file.filename)

        original_path = os.path.join(
            Config.UPLOAD_FOLDER, "original", filename
        )
        os.makedirs(os.path.dirname(original_path), exist_ok=True)

        file.save(original_path)

        image = Image(
            user_id=user.id,
            original_filename=filename
        )
        db.session.add(image)
        db.session.commit()

        return redirect(url_for("main.index"))

    return render_template("index.html")
