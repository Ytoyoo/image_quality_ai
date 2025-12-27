import cv2
import numpy as np
from PIL import Image as PILImage



def analyze_sharpness(image_path: str) -> float:
    """
    Возвращает числовую оценку резкости изображения.
    Чем больше значение — тем резче изображение.
    """
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Не удалось загрузить изображение")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance = laplacian.var()

    return float(variance)

def analyze_motion_blur(image_path: str) -> float:
    """
    Возвращает оценку вероятности смаза.
    Чем больше значение — тем выше вероятность motion blur.
    """
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Не удалось загрузить изображение")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Градиенты по X и Y
    grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

    abs_x = np.mean(np.abs(grad_x))
    abs_y = np.mean(np.abs(grad_y))

    # Соотношение направлений
    blur_score = abs(abs_x - abs_y)

    return float(blur_score)

def analyze_image(file_path):
    # Загружаем изображение через OpenCV
    img = cv2.imread(file_path)

    # Конвертируем в оттенки серого для анализа
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Яркость — среднее значение пикселей
    brightness = np.mean(gray) / 255  # нормируем до 0-1

    # Резкость — variance of Laplacian
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    sharpness = np.tanh(sharpness / 1000)  # нормируем примерно 0-1

    # Размытость — обратное резкости
    blur = 1 - sharpness

    # Цветовой баланс — стандартное отклонение по каналам
    b, g, r = cv2.split(img)
    color_balance = 1 - np.mean([np.std(b), np.std(g), np.std(r)]) / 128  # нормируем

    return brightness, sharpness, blur, color_balance

