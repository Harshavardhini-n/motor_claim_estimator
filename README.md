# 🚗 Instant Motor Claim Estimator

AI-powered vehicle damage assessment and insurance claim estimation tool.

---

## 📁 Folder Structure

```
motor_claim_estimator/
├── app.py                  ← Main Streamlit app (run this)
├── requirements.txt        ← All dependencies
├── setup_project.py        ← Run once to train models
├── src/
│   ├── preprocessor.py     ← OpenCV image pipeline
│   ├── predictor.py        ← ML inference + fallback simulation
│   ├── train_model.py      ← Train RandomForest models
│   └── cost_engine.py      ← Cost calculation + business logic
├── models/                 ← Saved ML models (auto-created)
├── data/
│   ├── raw/                ← Put raw images here (optional)
│   └── processed/
└── assets/
```

---

## ⚡ Quick Start (Step by Step)

### Step 1 — Install Python
Download Python 3.10+ from https://python.org
During install, CHECK "Add Python to PATH"

### Step 2 — Open VS Code
- Open VS Code
- File → Open Folder → Select `motor_claim_estimator`
- Open Terminal: Terminal → New Terminal

### Step 3 — Create Virtual Environment
```bash
python -m venv venv
```

**Activate it:**
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

You should see `(venv)` in your terminal prompt.

### Step 4 — Install Dependencies
```bash
pip install -r requirements.txt
```
This takes 2–3 minutes. Wait for it to finish.

### Step 5 — Train ML Models (one-time setup)
```bash
python setup_project.py
```
This creates `models/` folder with trained .pkl files.
Expected output:
```
✅ Severity model accuracy: ~95%
✅ Parts model accuracy: ~92%
💾 Models saved to models/
```

### Step 6 — Run the App
```bash
streamlit run app.py
```
Browser opens automatically at http://localhost:8501

---

## 🖼️ Where to Get Test Images (FREE)

### Option A — Google Images
Search: "car bumper damage", "car accident door dent", "cracked windshield"
Download and save as JPG/PNG.

### Option B — Kaggle (FREE dataset, no cost)
1. Go to https://kaggle.com
2. Sign up (free)
3. Search: "car damage dataset"
4. Download: "Car Damage Detection Dataset" by Jaineel Mavani
5. Use images from test/ folder

### Option C — Use any car photo from your phone
The app works on any car damage image.

---

## ⚠️ Common Errors & Fixes

### Error: `ModuleNotFoundError: No module named 'cv2'`
```bash
pip install opencv-python-headless
```

### Error: `ModuleNotFoundError: No module named 'streamlit'`
```bash
pip install streamlit
```

### Error: `FileNotFoundError: models/severity_model.pkl`
Run setup first:
```bash
python setup_project.py
```

### Error: `Could not decode image`
- Make sure file is JPG/PNG (not WebP or HEIC)
- Convert using: https://cloudconvert.com

### Error: Port already in use
```bash
streamlit run app.py --server.port 8502
```

### Error: `venv\Scripts\activate` not working (Windows)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then run activate again.

---

## 🎯 Demo Script (for hackathon presentation)

1. Open app → show sidebar with cost table
2. Upload a bumper damage image
3. Point out: "OpenCV pipeline — grayscale, blur, Canny edges"
4. Show edge density metric
5. Show ML prediction JSON
6. Show cost breakdown table
7. Show AUTO_APPROVED green banner
8. Upload a severely damaged image → show MANUAL REVIEW
9. Download the text report
10. Show simulation mode toggle

---

## 🏆 Hackathon Talking Points

- **Real OpenCV pipeline** — not just display, actually computes edge density
- **Trained ML model** — RandomForest with 95%+ accuracy on synthetic data
- **Production-ready architecture** — modular, error-handled, fallback mode
- **Business logic** — mirrors real insurance workflows
- **Downloadable reports** — claim ID, timestamp, full breakdown
