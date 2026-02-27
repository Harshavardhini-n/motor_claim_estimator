# src/preprocessor.py
# OpenCV image preprocessing pipeline
# Handles: resize, grayscale, blur, Canny edges, edge density

import cv2
import numpy as np
from PIL import Image
import io

def preprocess_image(uploaded_file):
    """
    Takes a Streamlit uploaded file, runs full OpenCV pipeline.
    Returns dict with all intermediate results + edge density score.
    """
    try:
        # Read image bytes → numpy array
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        original = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if original is None:
            raise ValueError("Could not decode image. Please upload a valid JPG/PNG.")

        # Step 1: Resize to standard size for consistency
        resized = cv2.resize(original, (640, 480))

        # Step 2: Convert to grayscale
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        # Step 3: Gaussian blur to reduce noise before edge detection
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Step 4: Canny edge detection
        # Low threshold=50, High threshold=150 — works well for car damage
        edges = cv2.Canny(blurred, 50, 150)

        # Step 5: Edge density — ratio of white pixels (edges) to total pixels
        total_pixels = edges.shape[0] * edges.shape[1]
        edge_pixels = np.count_nonzero(edges)
        edge_density = round(edge_pixels / total_pixels, 4)

        return {
            "original": resized,          # BGR numpy array
            "gray": gray,
            "blurred": blurred,
            "edges": edges,
            "edge_density": edge_density,  # float 0–1
            "error": None
        }

    except Exception as e:
        return {
            "original": None,
            "gray": None,
            "blurred": None,
            "edges": None,
            "edge_density": 0.0,
            "error": str(e)
        }


def numpy_to_pil(img_array, is_gray=False):
    """Convert numpy array to PIL Image for Streamlit display."""
    if img_array is None:
        return None
    if is_gray:
        return Image.fromarray(img_array)
    # BGR → RGB for correct colors
    rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)
