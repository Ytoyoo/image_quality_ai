import cv2
import os


def enhance_brightness(image, alpha=1.2, beta=30):
    """
    alpha — контраст
    beta — яркость
    """
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)


def sharpen_image(image):
    kernel = [[0, -1, 0],
              [-1, 5, -1],
              [0, -1, 0]]
    kernel = cv2.UMat(cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
    return cv2.filter2D(image, -1, kernel)


def denoise_image(image):
    return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)


def process_image(image_path: str, actions: dict, output_dir: str) -> str:
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Не удалось загрузить изображение")

    if actions.get("enhance_brightness"):
        image = enhance_brightness(image)

    if actions.get("sharpen"):
        image = sharpen_image(image)

    if actions.get("denoise"):
        image = denoise_image(image)

    filename = os.path.basename(image_path)
    output_path = os.path.join(output_dir, f"processed_{filename}")

    cv2.imwrite(output_path, image)
    return output_path
