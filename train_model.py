# src/train_model.py
# Trains a RandomForest classifier to predict:
#   - damaged_parts (multi-label)
#   - severity (minor / moderate / severe)
# Uses SYNTHETIC training data since we have no labeled dataset.
# In production, replace with real annotated car damage images.

import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

# ── Feature: edge_density (float) → severity + parts prediction
# ── We simulate realistic distributions for hackathon purposes

PARTS = ["bumper", "headlight", "door", "windshield"]
SEVERITIES = ["minor", "moderate", "severe"]

def generate_synthetic_data(n_samples=2000):
    """
    Generate synthetic training data based on domain rules:
    - Low edge density  → minor damage, fewer parts
    - Mid edge density  → moderate damage
    - High edge density → severe damage, more parts
    """
    np.random.seed(42)
    X = []  # features
    y_severity = []
    y_parts = []  # binary array for each part

    for _ in range(n_samples):
        # Simulate edge density from 0.02 to 0.45
        ed = np.random.uniform(0.02, 0.45)

        # Add some noise features: brightness variance, contrast
        brightness_var = np.random.uniform(0.1, 0.9)
        contrast = np.random.uniform(0.1, 0.9)

        X.append([ed, brightness_var, contrast])

        # Assign severity based on edge density ranges
        if ed < 0.12:
            sev = "minor"
            # Minor: 1-2 parts damaged, usually bumper or headlight
            parts = np.zeros(4)
            n_parts = np.random.randint(1, 3)
            chosen = np.random.choice([0, 1], size=n_parts, replace=False)
            parts[chosen] = 1

        elif ed < 0.28:
            sev = "moderate"
            parts = np.zeros(4)
            n_parts = np.random.randint(2, 4)
            chosen = np.random.choice(4, size=n_parts, replace=False)
            parts[chosen] = 1

        else:
            sev = "severe"
            parts = np.zeros(4)
            n_parts = np.random.randint(3, 5)
            chosen = np.random.choice(4, size=n_parts, replace=False)
            parts[chosen] = 1

        y_severity.append(sev)
        y_parts.append(parts)

    return (
        np.array(X),
        np.array(y_severity),
        np.array(y_parts)
    )


def train_and_save():
    """Train both models and save to models/ directory."""
    print("🔧 Generating synthetic training data...")
    X, y_sev, y_parts = generate_synthetic_data(2000)

    # ── Severity model ──
    le = LabelEncoder()
    y_sev_enc = le.fit_transform(y_sev)

    X_tr, X_te, ys_tr, ys_te = train_test_split(X, y_sev_enc, test_size=0.2, random_state=42)

    sev_model = RandomForestClassifier(n_estimators=100, random_state=42)
    sev_model.fit(X_tr, ys_tr)
    sev_acc = sev_model.score(X_te, ys_te)
    print(f"✅ Severity model accuracy: {sev_acc:.2%}")

    # ── Parts model (multi-label) ──
    X_tr2, X_te2, yp_tr, yp_te = train_test_split(X, y_parts, test_size=0.2, random_state=42)

    base_clf = RandomForestClassifier(n_estimators=100, random_state=42)
    parts_model = MultiOutputClassifier(base_clf)
    parts_model.fit(X_tr2, yp_tr)
    parts_acc = parts_model.score(X_te2, yp_te)
    print(f"✅ Parts model accuracy: {parts_acc:.2%}")

    # ── Save ──
    os.makedirs("models", exist_ok=True)
    joblib.dump(sev_model,   "models/severity_model.pkl")
    joblib.dump(parts_model, "models/parts_model.pkl")
    joblib.dump(le,          "models/label_encoder.pkl")
    print("💾 Models saved to models/")


if __name__ == "__main__":
    train_and_save()
