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
    old_session = ProcessingSession.query.get_or_404(session_id)
    image = old_session.image

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    image_path = os.path.join(upload_dir, image.original_filename)

    # Анализируем заново (на случай, если пользователь изменил что-то)
    metrics = analyze_image(image_path)

    # Создаём НОВУЮ сессию для этой обработки
    new_session = ProcessingSession(
        image_id=image.id,
        brightness_score=metrics["brightness"],
        sharpness_score=metrics["sharpness"],
        blur_score=metrics["noise"],
        color_balance_score=metrics["contrast"],
    )
    db.session.add(new_session)
    db.session.commit()  # commit, чтобы получить new_session.id

    actions = {
        "enhance_brightness": "enhance_brightness" in request.form,
        "sharpen": "sharpen" in request.form,
        "denoise": "denoise" in request.form,
        "auto_improve": "auto_improve" in request.form,
    }

    processed_filename = process_image(
        image_path=image_path,
        actions=actions,
        output_dir=upload_dir,
        metrics={
            "brightness": new_session.brightness_score,
            "sharpness": new_session.sharpness_score,
            "noise": new_session.blur_score,
            "contrast": new_session.color_balance_score,
        }
    )

    # Verdict и confidence
    summary = []
    if actions.get("auto_improve"):
        summary.append("Автоматический адаптивный режим")
    if actions.get("enhance_brightness"):
        summary.append("Повышена яркость")
    if actions.get("sharpen"):
        summary.append("Улучшена резкость")
    if actions.get("denoise"):
        summary.append("Убран шум")

    verdict = " • ".join(summary) if summary else "Ничего не применено"
    confidence = round(len(summary) / 4, 2)

    result = Result(
        session_id=new_session.id,  # ← привязываем к новой сессии
        processed_filename=processed_filename,
        quality_score=confidence,
        verdict=verdict
    )
    db.session.add(result)
    db.session.commit()

    return redirect(url_for("main.show_result", result_id=result.id))


@main_bp.route("/image/<int:image_id>/history")
def image_history(image_id):
    image = Image.query.get_or_404(image_id)
    sessions = ProcessingSession.query.filter_by(image_id=image_id).order_by(ProcessingSession.created_at.desc()).all()
    return render_template("history.html", image=image, sessions=sessions)


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

