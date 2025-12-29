import cv2
import numpy as np


def load_gray(image_path: str):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Не удалось загрузить изображение")
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def calculate_sharpness(image_path: str) -> float:
    gray = load_gray(image_path)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def calculate_brightness(image_path: str) -> float:
    gray = load_gray(image_path)
    return float(np.mean(gray))


def calculate_contrast(image_path: str) -> float:
    gray = load_gray(image_path)
    return float(np.std(gray))


def calculate_noise(image_path: str) -> float:
    """
    Приближённая оценка шума:
    разница между изображением и блюром
    """
    gray = load_gray(image_path)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    noise = np.mean(np.abs(gray - blurred))
    return float(noise)


def analyze_image(image_path: str) -> dict:
    """
    Полный анализ изображения
    """
    return {
        "sharpness": calculate_sharpness(image_path),
        "brightness": calculate_brightness(image_path),
        "contrast": calculate_contrast(image_path),
        "noise": calculate_noise(image_path),
    }
