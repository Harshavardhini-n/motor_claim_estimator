#!/usr/bin/env python3
# setup_project.py
# Run this ONCE to: verify structure + train ML models
# Usage: python setup_project.py
import os
import sys

def create_dirs():
    dirs = ["src", "models", "data/raw", "data/processed", "tests", "assets"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print("✅ Folder structure ready")

def train_models():
    print("\n🤖 Training ML models...")
    sys.path.insert(0, "src")
    from train_model import train_and_save
    train_and_save()
    print("✅ Models trained and saved!")

def verify_files():
    required = [
        "app.py",
        "src/preprocessor.py",
        "src/predictor.py",
        "src/cost_engine.py",
        "src/train_model.py",
        "requirements.txt",
        "models/severity_model.pkl",
        "models/parts_model.pkl",
        "models/label_encoder.pkl",
    ]
    print("\n🔍 Verifying all files...")
    all_ok = True
    for f in required:
        exists = os.path.exists(f)
        status = "✅" if exists else "❌"
        print(f"  {status} {f}")
        if not exists:
            all_ok = False
    return all_ok

if __name__ == "__main__":
    print("=" * 50)
    print("   INSTANT MOTOR CLAIM ESTIMATOR — SETUP")
    print("=" * 50)
    create_dirs()
    train_models()
    ok = verify_files()
    print()
    if ok:
        print("🎉 Setup complete! Run: streamlit run app.py")
    else:
        print("⚠️  Some files missing. Check errors above.")
