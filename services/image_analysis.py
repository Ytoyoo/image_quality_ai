import cv2
import numpy as np
from skimage import restoration
from skimage import exposure
from skimage import filters
from scipy.stats import entropy


def load_gray(image_path: str):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Не удалось загрузить изображение")
    # Добавим resize для consistency (например, до 512x512 max), чтобы метрики были сравнимы
    height, width = image.shape[:2]
    if max(height, width) > 512:
        scale = 512 / max(height, width)
        image = cv2.resize(image, (int(width * scale), int(height * scale)))
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def calculate_sharpness(image_path: str) -> float:
    gray = load_gray(image_path)
    # Улучшенная резкость: variance Laplacian + normalization
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    # Добавим edge detection с Sobel для лучшей оценки
    sobel = filters.sobel(gray)
    sobel_var = np.var(sobel)
    # Комбинируем: среднее, нормализуем в 0-100 (эмпирически: good ~1000+ lap, sobel ~0.01+)
    combined = (lap_var + sobel_var * 100) / 2  # Scale sobel
    score = min(100, np.log1p(combined) * 10)  # Log для сжатия диапазона, подгони по тестам
    return float(score)


def calculate_brightness(image_path: str) -> float:
    gray = load_gray(image_path)
    # Улучшенно: не просто mean, а с учетом exposure
    mean_bright = np.mean(gray)
    # Проверяем underexposed/overexposed с histogram
    hist = exposure.histogram(gray)[0]
    entropy_val = entropy(hist + 1e-10)  # Entropy для динамического диапазона
    # Нормализуем в 0-100, корректируем на entropy (high entropy = better distribution)
    score = (mean_bright / 255 * 100) * (entropy_val / np.log2(256))  # Normalize entropy to 0-1
    return float(min(100, max(0, score)))


def calculate_contrast(image_path: str) -> float:
    gray = load_gray(image_path)
    # Улучшенно: RMS contrast = std / mean (normalized)
    if np.mean(gray) == 0:
        return 0.0
    rms_contrast = np.std(gray) / np.mean(gray)
    # Добавим check low contrast от skimage
    is_low = exposure.is_low_contrast(gray)
    # Нормализуем в 0-100: typical good RMS ~0.2-0.5, scale
    score = rms_contrast * 200  # Пример: 0.5 -> 100
    if is_low:
        score *= 0.5  # Penalty за low contrast
    return float(min(100, max(0, score)))


def calculate_noise(image_path: str) -> float:
    """
    Улучшенная оценка шума: используем wavelet-based estimation из skimage
    """
    gray = load_gray(image_path)
    # estimate_sigma возвращает std шума (Gaussian assumption)
    sigma = restoration.estimate_sigma(gray, average_sigmas=True, channel_axis=None)
    # Нормализуем: low noise ~0-5, high >20, invert to score 0-100 (higher = less noise)
    score = max(0, 100 - (sigma * 5))  # Scale: sigma=20 -> 0, sigma=0 ->100, подгони
    return float(score)


def calculate_color_balance(image_path: str) -> float:
    """
    Новая функция для баланса цвета (поскольку в HTML есть score)
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Не удалось загрузить изображение")
    # Конверт в HSV для saturation
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    saturation_mean = np.mean(hsv[:,:,1])
    # Баланс каналов: std means RGB (low std = balanced)
    means = np.mean(image, axis=(0,1))
    balance_std = np.std(means)
    # Colorfulness: sqrt( std(RG)^2 + std(YB)^2 ) + 0.3 * mean( std(RG) + std(YB) ) но упростим
    # Нормализуем в 0-100: high saturation good, low balance_std good
    score = (saturation_mean / 255 * 50) + max(0, 50 - balance_std)
    return float(score)


def analyze_image(image_path: str) -> dict:
    """
    Полный анализ изображения: улучшенный с нормализацией в scores 0-100
    """
    analysis = {
        "sharpness": calculate_sharpness(image_path),
        "brightness": calculate_brightness(image_path),
        "contrast": calculate_contrast(image_path),
        "noise": calculate_noise(image_path),
        "color_balance": calculate_color_balance(image_path),
    }

    analysis["overall_quality"] = np.mean(list(analysis.values()))
    return analysis