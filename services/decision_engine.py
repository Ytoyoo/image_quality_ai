def recommend_actions(analysis: dict) -> dict:
    actions = {
        "enhance_brightness": False,
        "sharpen": False,
        "denoise": False,
        "confidence": 0.0,
        "summary": []
    }

    score = 0
    total = 0

    # Яркость
    total += 1
    if analysis["brightness"] < 90:
        actions["enhance_brightness"] = True
        actions["summary"].append("Изображение слишком тёмное")
        score += 1

    # Резкость
    total += 1
    if analysis["sharpness"] < 100:
        actions["sharpen"] = True
        actions["summary"].append("Низкая резкость")
        score += 1

    # Шум
    total += 1
    if analysis["noise"] > 15:
        actions["denoise"] = True
        actions["summary"].append("Присутствует шум")
        score += 1

    actions["confidence"] = round(score / total, 2)
    return actions
