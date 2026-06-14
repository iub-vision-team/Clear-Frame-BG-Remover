"""
utils.py — AI Background Removal Utility
=========================================
This module contains all background-removal logic, keeping it completely
separate from views (separation of concerns / Django best practice).

How the AI model works (simple explanation for viva):
------------------------------------------------------
We use the `rembg` library which wraps the U2Net deep learning model.

U2Net (U-squared Network) is a convolutional neural network architecture
designed specifically for salient object detection — meaning it detects
the most important object in an image (usually the foreground subject).

Steps the model performs:
  1. The input image is resized and normalised for the neural network.
  2. The image passes through multiple nested U-Net encoder–decoder stages.
     Each stage captures features at different scales (fine textures to
     broad shapes), producing multi-scale "saliency maps".
  3. The maps are fused and a final probability mask is produced — each
     pixel gets a value 0–1 indicating how likely it is to be foreground.
  4. The mask is thresholded: pixels above ~0.5 stay, the rest become
     transparent (alpha = 0).
  5. rembg applies this alpha mask to the original image and returns a
     PNG with a transparent background.

The model was pre-trained on the DUTS-TR dataset (~10,500 labelled images)
and can separate people, products, animals, and objects from backgrounds
with high accuracy — all without any manual selection.
"""

import os
import io
import uuid
import logging
from pathlib import Path

from PIL import Image

logger = logging.getLogger(__name__)

_IMAGENET_MODEL = None
_ANIMAL_MODEL = None
_ANIMAL_CLASS_NAMES = None

ML_MODELS_DIR = Path(__file__).resolve().parent / "ml_models"
ANIMAL_MODEL_PATH = ML_MODELS_DIR / "animal_classifier.keras"
ANIMAL_CLASSES_PATH = ML_MODELS_DIR / "animal_classes.json"


def _load_animal_class_names() -> list[str]:
    """Load custom animal class names exported from the Kaggle notebook."""
    global _ANIMAL_CLASS_NAMES

    if _ANIMAL_CLASS_NAMES is not None:
        return _ANIMAL_CLASS_NAMES

    try:
        import json

        with open(ANIMAL_CLASSES_PATH, "r", encoding="utf-8") as class_file:
            class_names = json.load(class_file)

        if not isinstance(class_names, list) or not all(isinstance(name, str) for name in class_names):
            logger.warning("Animal class file must contain a JSON list of strings.")
            _ANIMAL_CLASS_NAMES = []
        else:
            _ANIMAL_CLASS_NAMES = class_names
    except FileNotFoundError:
        _ANIMAL_CLASS_NAMES = []
    except Exception as exc:
        logger.exception("Could not load animal class names: %s", exc)
        _ANIMAL_CLASS_NAMES = []

    return _ANIMAL_CLASS_NAMES


def predict_animal_classes(image_file, top=3) -> list[dict]:
    """
    Predict animal classes with a custom Kaggle-trained model when available.

    Required files:
      remover/ml_models/animal_classifier.keras
      remover/ml_models/animal_classes.json
    """
    global _ANIMAL_MODEL

    class_names = _load_animal_class_names()
    if not ANIMAL_MODEL_PATH.exists() or not class_names:
        return []

    try:
        import cv2
        import numpy as np
        from tensorflow.keras.models import load_model
    except ImportError as exc:
        logger.warning("Animal prediction dependencies are unavailable: %s", exc)
        return []

    try:
        image_file.seek(0)
        raw_bytes = np.frombuffer(image_file.read(), np.uint8)
        image_file.seek(0)

        image = cv2.imdecode(raw_bytes, cv2.IMREAD_COLOR)
        if image is None:
            return []

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (256, 256), interpolation=cv2.INTER_AREA)
        batch = np.expand_dims(image.astype("float32"), axis=0)

        if _ANIMAL_MODEL is None:
            _ANIMAL_MODEL = load_model(ANIMAL_MODEL_PATH)

        prediction_values = _ANIMAL_MODEL.predict(batch, verbose=0)[0]
        if len(prediction_values) != len(class_names):
            logger.warning(
                "Animal model output count (%s) does not match class count (%s).",
                len(prediction_values),
                len(class_names),
            )
            return []

        ranked_indexes = np.argsort(prediction_values)[::-1][:top]
        return [
            {
                "class_id": class_names[index].lower().replace(" ", "_"),
                "label": class_names[index],
                "confidence": round(float(prediction_values[index]) * 100, 2),
                "source": "Custom Animal Model",
            }
            for index in ranked_indexes
        ]
    except Exception as exc:
        logger.exception("Animal prediction failed: %s", exc)
        image_file.seek(0)
        return []


def predict_image_classes(image_file, top=3) -> list[dict]:
    """
    Predict the uploaded image class using TensorFlow MobileNetV2/ImageNet.

    TensorFlow, NumPy, and OpenCV are optional runtime dependencies here. If
    they are missing, background removal still works and prediction is skipped.
    """
    global _IMAGENET_MODEL

    animal_predictions = predict_animal_classes(image_file, top=top)
    if animal_predictions:
        return animal_predictions

    try:
        import cv2
        import numpy as np
        from tensorflow.keras.applications.mobilenet_v2 import (
            MobileNetV2,
            decode_predictions,
            preprocess_input,
        )
    except ImportError as exc:
        logger.warning("Image prediction dependencies are unavailable: %s", exc)
        return []

    try:
        image_file.seek(0)
        raw_bytes = np.frombuffer(image_file.read(), np.uint8)
        image_file.seek(0)

        image = cv2.imdecode(raw_bytes, cv2.IMREAD_COLOR)
        if image is None:
            return []

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
        batch = np.expand_dims(image.astype("float32"), axis=0)
        batch = preprocess_input(batch)

        if _IMAGENET_MODEL is None:
            _IMAGENET_MODEL = MobileNetV2(weights="imagenet")

        prediction_values = _IMAGENET_MODEL.predict(batch, verbose=0)
        decoded_predictions = decode_predictions(prediction_values, top=top)[0]

        return [
            {
                "class_id": class_id,
                "label": label.replace("_", " ").title(),
                "confidence": round(float(confidence) * 100, 2),
                "source": "ImageNet",
            }
            for class_id, label, confidence in decoded_predictions
        ]
    except Exception as exc:
        logger.exception("Image prediction failed: %s", exc)
        image_file.seek(0)
        return []


def remove_background(input_image_file) -> bytes:
    """
    Remove the background from an uploaded image file using rembg + U2Net.

    Args:
        input_image_file: A Django InMemoryUploadedFile or similar file-like object.

    Returns:
        bytes: PNG image data with transparent background.

    Raises:
        RuntimeError: If background removal fails for any reason.
    """
    try:
        from rembg import remove  # imported here so the app still loads if rembg is not yet installed

        # Read the uploaded file into bytes
        input_bytes = input_image_file.read()
        input_image_file.seek(0)  # reset file pointer so Django can still save it

        # Run U2Net background removal
        output_bytes = remove(input_bytes)
        return output_bytes

    except ImportError:
        raise RuntimeError(
            "rembg is not installed. Run: pip install rembg"
        )
    except Exception as exc:
        logger.exception("Background removal failed: %s", exc)
        raise RuntimeError(f"Background removal failed: {exc}") from exc


def save_processed_image(output_bytes: bytes, save_dir: str) -> str:
    """
    Save the processed (background-removed) PNG bytes to a file on disk.

    Args:
        output_bytes: PNG bytes returned by remove_background().
        save_dir:     Absolute path to the directory where the file should be saved.

    Returns:
        str: Relative path from MEDIA_ROOT, e.g. "processed/abc123.png"
             suitable for storing in an ImageField.
    """
    os.makedirs(save_dir, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.png"
    abs_path = os.path.join(save_dir, filename)

    # Convert raw bytes → PIL Image → save as PNG (preserves transparency)
    image = Image.open(io.BytesIO(output_bytes))
    image.save(abs_path, format='PNG')

    # Return the relative path for the ImageField
    relative_path = os.path.join('processed', filename)
    return relative_path


def validate_image_extension(filename: str) -> bool:
    """Return True if filename has an allowed image extension."""
    allowed = {'.jpg', '.jpeg', '.png'}
    ext = Path(filename).suffix.lower()
    return ext in allowed


def get_image_info(image_file) -> dict:
    """
    Return basic info about an uploaded image (format, size, dimensions).
    Useful for logging / admin display.
    """
    try:
        image_file.seek(0)
        img = Image.open(image_file)
        info = {
            'format': img.format,
            'mode': img.mode,
            'width': img.width,
            'height': img.height,
            'size_bytes': image_file.size,
        }
        image_file.seek(0)
        return info
    except Exception:
        return {}
