import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from flask import send_file
from werkzeug.utils import secure_filename

from extensions import db

from models.image import Image
from models.result import Result
from models.processing_session import ProcessingSession

from services.image_analysis import analyze_image
from services.image_processing import process_image
from services.decision_engine import recommend_actions

main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET", "POST"])
def upload_image():
    if request.method == "POST":
        file = request.files.get("image")

        if not file or file.filename == "":
            return "Файл не выбран", 400

        filename = secure_filename(file.filename)

        upload_dir = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        # ❗ временно user_id = 1
        image = Image(
            user_id=1,
            original_filename=filename,
        )
        db.session.add(image)
        db.session.commit()

        return redirect(url_for("main.analyze_image_route", image_id=image.id))

    return render_template("upload.html")


@main_bp.route("/analyze/<int:image_id>")
def analyze_image_route(image_id):
    image = Image.query.get_or_404(image_id)

    image_path = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        image.original_filename
    )

    # Анализируем изображение
    metrics = analyze_image(image_path)

    # Создаём сессию с метриками
    session = ProcessingSession(
        image_id=image.id,
        brightness_score=metrics["brightness"],
        sharpness_score=metrics["sharpness"],
        blur_score=metrics["noise"],
        color_balance_score=metrics["contrast"],
    )
    db.session.add(session)
    db.session.commit()

    # Здесь НЕ делаем улучшение и НЕ создаём Result
    # Просто рендерим страницу с метриками
    return render_template(
        "analysis.html",   # ← новая страница или та же result.html, но без processed_filename
        image=image,
        session=session,
        metrics=metrics
    )

@main_bp.route("/process/<int:session_id>", methods=["POST"])
def process_image_service(session_id):
    session = ProcessingSession.query.get_or_404(session_id)
    image = session.image

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    image_path = os.path.join(upload_dir, image.original_filename)

    # действия ИЗ ФОРМЫ
    actions = {
        "enhance_brightness": "enhance_brightness" in request.form,
        "sharpen": "sharpen" in request.form,
        "denoise": "denoise" in request.form,
        "confidence": 0.0,
        "summary": []
    }

    # summary для Result
    if actions["enhance_brightness"]:
        actions["summary"].append("Повышена яркость")
    if actions["sharpen"]:
        actions["summary"].append("Повышена резкость")
    if actions["denoise"]:
        actions["summary"].append("Удалён шум")

    actions["confidence"] = round(
        sum(actions[k] for k in ["enhance_brightness", "sharpen", "denoise"]) / 3,
        2
    )

    # обработка
    output_path = process_image(
        image_path=image_path,
        actions=actions,
        output_dir=upload_dir
    )

    result = Result(
        session_id=session.id,
        processed_filename=os.path.basename(output_path),
        quality_score=actions["confidence"],
        verdict="; ".join(actions["summary"])
    )

    db.session.add(result)
    db.session.commit()

    return redirect(url_for("main.show_result", result_id=result.id))


@main_bp.route("/image/<int:image_id>/history")
def image_history(image_id):
    image = Image.query.get_or_404(image_id)

    sessions = (
        ProcessingSession.query
        .filter_by(image_id=image.id)
        .order_by(ProcessingSession.created_at.desc())
        .all()
    )

    return render_template(
        "history.html",
        image=image,
        sessions=sessions
    )


@main_bp.route("/result/<int:result_id>")
def show_result(result_id):
    result = Result.query.get_or_404(result_id)
    session = result.session
    image = session.image

    upload_dir = current_app.config["UPLOAD_FOLDER"]

    original_path = os.path.join(upload_dir, image.original_filename)
    processed_path = os.path.join(upload_dir, result.processed_filename)

    # ОРИГИНАЛЬНЫЕ МЕТРИКИ — из ProcessingSession (уже в БД)
    original_metrics = {
        "brightness": session.brightness_score,
        "sharpness": session.sharpness_score,
        "noise": session.blur_score,
        "contrast": session.color_balance_score,
    }

    # НОВЫЕ МЕТРИКИ — считаем ЗДЕСЬ
    processed_metrics = analyze_image(processed_path)

    return render_template(
        "result.html",
        image=image,
        result=result,
        original_metrics=original_metrics,
        processed_metrics=processed_metrics
    )

