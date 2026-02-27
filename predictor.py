# src/predictor.py
# FINAL CLEAN STABLE VERSION
# Deterministic | No hallucination | No dominance bug | Hackathon safe

import numpy as np
import cv2
import json
import traceback

PARTS = ["bumper", "headlight", "door", "windshield"]

# ==========================================================
# MAIN ENTRY
# ==========================================================

def predict(preprocessed: dict) -> dict:
    try:
        return _opencv_predict(preprocessed)
    except Exception as e:
        return _safe_fallback(preprocessed, str(e))

# ==========================================================
# SAFE FALLBACK
# ==========================================================

def _safe_fallback(preprocessed, error_msg):
    return {
        "damaged_parts": [],
        "severity": "no_damage",
        "confidence_score": 60,
        "edge_density": float(preprocessed.get("edge_density", 0)),
        "damage_score": 0.0,
        "zone_scores": {},
        "features": {},
        "mode": "SAFE_FALLBACK",
        "error": error_msg,
    }

# ==========================================================
# CORE OPENCV ENGINE
# ==========================================================

def _opencv_predict(preprocessed):

    gray = preprocessed.get("gray")
    edges = preprocessed.get("edges")

    if gray is None or edges is None:
        return _simulate(preprocessed.get("edge_density", 0))

    h, w = gray.shape
    zones = _build_zones(h, w)

    zone_scores = {}

    for part, (y1, y2, x1, x2) in zones.items():
        roi_gray = gray[y1:y2, x1:x2]
        roi_edges = edges[y1:y2, x1:x2]

        if roi_gray.size == 0:
            zone_scores[part] = 0.0
            continue

        zone_scores[part] = _score_zone(roi_gray, roi_edges, part)

    # Select highest scoring zone
    primary_part = max(zone_scores, key=zone_scores.get)
    primary_score = zone_scores[primary_part]
    if primary_part == "windshield":
        # Only allow windshield if very strong
        if primary_score < 0.40:
            non_ws = {k: v for k, v in zone_scores.items() if k != "windshield"}
            primary_part = max(non_ws, key=non_ws.get)
            primary_score = non_ws[primary_part]
    # If extremely low overall → no damage
    if primary_score < 0.05:
        return _no_damage(preprocessed, zone_scores)

    severity = _classify(primary_score)

    return {
        "damaged_parts": [primary_part],
        "severity": severity,
        "confidence_score": int(min(95, 70 + primary_score * 30)),
        "edge_density": float(preprocessed.get("edge_density", 0)),
        "damage_score": round(primary_score, 3),
        "zone_scores": {k: round(v, 3) for k, v in zone_scores.items()},
        "features": {},
        "mode": "OPENCV_STABLE",
        "error": None
    }

# ==========================================================
# NO DAMAGE STRUCTURE
# ==========================================================

def _no_damage(preprocessed, zone_scores):
    return {
        "damaged_parts": [],
        "severity": "no_damage",
        "confidence_score": 70,
        "edge_density": float(preprocessed.get("edge_density", 0)),
        "damage_score": 0.0,
        "zone_scores": {k: round(v, 3) for k, v in zone_scores.items()},
        "features": {},
        "mode": "OPENCV_STABLE",
        "error": None
    }

# ==========================================================
# ZONE DEFINITIONS
# ==========================================================

def _build_zones(h, w):
    return {
        # Top-left small area
        "headlight":  (0, int(h*0.22), 0, int(w*0.25)),

        # STRICT windshield: ONLY upper-middle narrow band
        "windshield": (
            0,
            int(h*0.28),          # only top 28%
            int(w*0.38),          # center region only
            int(w*0.62)
        ),

        # Door starts LOWER so it never overlaps windshield
        "door": (
            int(h*0.35),          # starts below windshield
            int(h*0.75),
            int(w*0.15),
            int(w*0.85)
        ),

        # Bottom area
        "bumper": (
            int(h*0.75),
            h,
            int(w*0.05),
            int(w*0.95)
        ),
    }

# ==========================================================
# SMART SCORING (NO ZEROING LOGIC)
# ==========================================================

def _score_zone(gray, edges, part):

    edge_density = np.count_nonzero(edges) / max(edges.size, 1)

    lap = cv2.Laplacian(gray, cv2.CV_64F)
    lap_var = np.var(lap) / 1000.0

    intensity_std = np.std(gray) / 255.0

    base_score = edge_density * 0.5 + lap_var * 0.3 + intensity_std * 0.2

    # Special windshield crack amplification
    if part == "windshield":
        lines = cv2.HoughLinesP(
            edges,
            1,
            np.pi/180,
            threshold=50,
            minLineLength=25,
            maxLineGap=8
        )
        if lines is not None:
            crack_factor = min(len(lines) * 0.01, 0.4)
            base_score += crack_factor

    return float(min(base_score, 1.0))

# ==========================================================
# SEVERITY CALIBRATION
# ==========================================================

def _classify(score):

    if score < 0.15:
        return "minor"
    elif score < 0.45:
        return "moderate"
    else:
        return "severe"

# ==========================================================
# SIMULATION MODE
# ==========================================================

def _simulate(edge_density=0.05):

    if edge_density < 0.05:
        sev, parts = "no_damage", []
    elif edge_density < 0.15:
        sev, parts = "minor", ["bumper"]
    elif edge_density < 0.30:
        sev, parts = "moderate", ["door"]
    else:
        sev, parts = "severe", ["bumper"]

    return {
        "damaged_parts": parts,
        "severity": sev,
        "confidence_score": 75,
        "edge_density": float(edge_density),
        "damage_score": float(edge_density),
        "zone_scores": {},
        "features": {},
        "mode": "SIMULATION",
        "error": None,
    }

# ==========================================================
# JSON FORMATTER
# ==========================================================

def prediction_to_json(result):
    return json.dumps(result, indent=2)