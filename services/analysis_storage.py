from extensions import db
from models.image_analysis import ImageAnalysis


def save_analysis(image_id: int, analysis_data: dict) -> ImageAnalysis:
    analysis = ImageAnalysis(
        image_id=image_id,
        sharpness=analysis_data["sharpness"],
        brightness=analysis_data["brightness"],
        contrast=analysis_data["contrast"],
        noise=analysis_data["noise"],
    )

    db.session.add(analysis)
    db.session.commit()

    return analysis
