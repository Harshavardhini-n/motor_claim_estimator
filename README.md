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

orts** — claim ID, timestamp, full breakdown
