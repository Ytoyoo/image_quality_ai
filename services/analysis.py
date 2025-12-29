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

