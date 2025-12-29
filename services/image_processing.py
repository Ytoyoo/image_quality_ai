import cv2
import numpy as np
import os


def adjust_brightness(image):
    """Только яркость — gamma + shift, без потери контраста"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    current_mean = np.mean(gray)
    target_mean = 115

    # Gamma-коррекция
    gamma = 1.0
    if current_mean < 70:
        gamma = 1.0 + (70 - current_mean) / 140.0 * 0.6  # max ~1.3
    elif current_mean > 160:
        gamma = 1.0 - (current_mean - 160) / 140.0 * 0.3  # min ~0.8

    lut = np.array([((i / 255.0) ** (1.0 / gamma)) * 255 for i in np.arange(0, 256)]).astype("uint8")
    image_gamma = cv2.LUT(image, lut)

    # Мягкий сдвиг
    current_mean_after = np.mean(cv2.cvtColor(image_gamma, cv2.COLOR_BGR2GRAY))
    delta = target_mean - current_mean_after
    delta = np.clip(delta, -30, 30)

    return cv2.convertScaleAbs(image_gamma, alpha=1.0, beta=delta)


def enhance_contrast(image, clip_limit=1.8):
    """CLAHE для контраста (только в auto-режиме, если нужно)"""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
    l_clahe = clahe.apply(l)

    # Смешиваем 70% оригинал + 30% CLAHE → минимальная потеря контраста
    l_mix = cv2.addWeighted(l, 0.7, l_clahe, 0.3, 0)

    lab_enhanced = cv2.merge([l_mix, a, b])
    return cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)


def sharpen_image(image, strength=0.8):
    blurred = cv2.GaussianBlur(image, (0, 0), sigmaX=2.5)
    sharpened = cv2.addWeighted(image, 1 + strength, blurred, -strength, 0)
    return np.clip(sharpened, 0, 255).astype(np.uint8)


def denoise_image(image, strength=45):
    return cv2.bilateralFilter(image, d=7, sigmaColor=strength, sigmaSpace=55)


def process_image(image_path: str, actions: dict, output_dir: str, metrics: dict = None) -> str:
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Не удалось загрузить изображение")

    thresholds = {"brightness": 65, "contrast": 65, "sharpness": 70, "noise": 70}

    # Определяем, что применять
    apply_brightness = actions.get("enhance_brightness", False)
    apply_sharpen = actions.get("sharpen", False)
    apply_denoise = actions.get("denoise", False)
    apply_contrast = False  # CLAHE только в auto

    if actions.get("auto_improve", False) and metrics:
        apply_brightness = metrics.get("brightness", 100) < thresholds["brightness"]
        apply_contrast = metrics.get("contrast", 100) < thresholds["contrast"]
        apply_sharpen = metrics.get("sharpness", 100) < thresholds["sharpness"]
        apply_denoise = metrics.get("noise", 100) < thresholds["noise"]

        # Сила
        brightness_strength = 1.0 if apply_brightness else 0
        contrast_clip = 1.5 + (thresholds["contrast"] - metrics.get("contrast", 100)) / 50 if apply_contrast else 0
        sharpen_strength = 0.6 + (thresholds["sharpness"] - metrics.get("sharpness", 100)) / 140 if apply_sharpen else 0
        denoise_strength = 30 + (thresholds["noise"] - metrics.get("noise", 100)) * 0.6 if apply_denoise else 0

    else:
        # Ручной: фиксированные мягкие значения
        brightness_strength = 1.0
        contrast_clip = 1.8
        sharpen_strength = 0.8
        denoise_strength = 45

    # Порядок
    if apply_denoise:
        image = denoise_image(image, strength=int(denoise_strength))

    if apply_brightness:
        image = adjust_brightness(image)

    if apply_contrast:
        image = enhance_contrast(image, clip_limit=contrast_clip)

    if apply_sharpen:
        image = sharpen_image(image, strength=sharpen_strength)

    filename = os.path.basename(image_path)
    output_filename = f"processed_{filename}"
    output_path = os.path.join(output_dir, output_filename)

    cv2.imwrite(output_path, image)
    return output_filename