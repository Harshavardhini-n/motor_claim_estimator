# app.py
# Main Streamlit application — Instant Motor Claim Estimator
# Run with: streamlit run app.py

import streamlit as st
import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from preprocessor import preprocess_image, numpy_to_pil
from predictor import predict, prediction_to_json
from cost_engine import estimate_cost, generate_text_report

# ── Page Configuration ──────────────────────────────────────
st.set_page_config(
    page_title="Instant Motor Claim Estimator",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS for professional look ────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
        padding: 2rem; border-radius: 12px;
        color: white; text-align: center; margin-bottom: 2rem;
    }
    .decision-approved {
        background: #d4edda; border-left: 6px solid #28a745;
        padding: 1rem; border-radius: 8px; margin: 1rem 0;
        color: #155724; font-weight: bold;
    }
    .decision-review {
        background: #fff3cd; border-left: 6px solid #ffc107;
        padding: 1rem; border-radius: 8px; margin: 1rem 0;
        color: #856404; font-weight: bold;
    }
    .cost-table { font-size: 1.1rem; }
    .stMetric label { font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ─────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/car-damage.png", width=80)
    st.title("⚙️ Settings")
    st.markdown("---")

    # Ollama status
    st.markdown("### 🤖 AI Vision Engine")
    try:
        import ollama
        installed = [m["name"] for m in ollama.list()["models"]]
        vision_models = ["llava:13b", "llava", "moondream", "llava:7b"]
        active = next((m for m in vision_models if any(m in i for i in installed)), None)
        if active:
            st.success(f"✅ Active: `{active}`")
        else:
            st.warning("No vision model found")
            st.code("ollama pull llava:13b", language="bash")
            st.caption("Or for low RAM: `ollama pull moondream`")
    except Exception:
        st.info("📥 Install Ollama from ollama.com\nthen run:\n`ollama pull llava:13b`")
    st.markdown("---")

    force_simulation = st.toggle(
        "Force Simulation Mode",
        value=False,
        help="Use rule-based simulation instead of ML model"
    )

    st.markdown("---")
    st.markdown("### 📋 Part Base Costs (₹)")
    st.markdown("""
    | Part | Cost |
    |---|---|
    | Bumper | ₹8,000 |
    | Headlight | ₹6,000 |
    | Door | ₹15,000 |
    | Windshield | ₹12,000 |
    """)

    st.markdown("---")
    st.markdown("### 🔢 Severity Multipliers")
    st.markdown("""
    | Severity | Multiplier |
    |---|---|
    | Minor | 1.0× |
    | Moderate | 1.8× |
    | Severe | 3.2× |
    """)

    st.markdown("---")
    st.markdown("### ✅ Auto-Approval Rules")
    st.info("Auto-approved when:\n- Total < ₹30,000\n- No severe damage")

    st.markdown("---")
    st.caption("Built with ❤️ using Python + Streamlit + OpenCV + ML")


# ── MAIN CONTENT ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🚗 Instant Motor Claim Estimator</h1>
    <p>AI-powered vehicle damage assessment & cost estimation</p>
</div>
""", unsafe_allow_html=True)

# ── Upload Section ───────────────────────────────────────────
col_upload, col_info = st.columns([2, 1])

with col_upload:
    st.subheader("📤 Upload Vehicle Damage Image")
    uploaded_file = st.file_uploader(
        "Upload a clear photo of the damaged vehicle",
        type=["jpg", "jpeg", "png", "bmp"],
        help="Best results with well-lit, close-up photos of damage"
    )

with col_info:
    st.subheader("ℹ️ Tips")
    st.markdown("""
    - 📸 Use well-lit photos
    - 🎯 Focus on damaged area
    - 🔍 Higher resolution = better detection
    - 📐 Include full damage in frame
    """)

# ── Processing ───────────────────────────────────────────────
if uploaded_file is not None:
    st.markdown("---")

    # ── Step 1: Preprocessing ──
    with st.spinner("🔍 Analyzing image with OpenCV..."):
        # Reset file pointer
        uploaded_file.seek(0)
        preprocessed = preprocess_image(uploaded_file)

    if preprocessed["error"]:
        st.error(f"❌ Image processing failed: {preprocessed['error']}")
        st.stop()

    # ── Step 2: Show preprocessed images ──
    st.subheader("🔬 OpenCV Preprocessing Pipeline")
    img_cols = st.columns(4)

    with img_cols[0]:
        st.image(numpy_to_pil(preprocessed["original"]), caption="Original", use_container_width=True)
    with img_cols[1]:
        st.image(numpy_to_pil(preprocessed["gray"], is_gray=True), caption="Grayscale", use_container_width=True)
    with img_cols[2]:
        st.image(numpy_to_pil(preprocessed["blurred"], is_gray=True), caption="Gaussian Blur", use_container_width=True)
    with img_cols[3]:
        st.image(numpy_to_pil(preprocessed["edges"], is_gray=True), caption="Canny Edges", use_container_width=True)

    # ── Step 3: ML Prediction ──
    with st.spinner("🤖 Analyzing damage... (first run may take 20–30 sec if using AI)"):
        if force_simulation:
            from predictor import _simulate
            prediction = _simulate(preprocessed.get("edge_density", 0.05))
            prediction["mode"] = "SIMULATION (Manual)"
        else:
            try:
                prediction = predict(preprocessed)
            except Exception as e:
                from predictor import _simulate
                prediction = _simulate(preprocessed.get("edge_density", 0.05))
                prediction["error"] = str(e)



    # ── Step 4: Cost Estimation ──
    report = estimate_cost(prediction)

    # ── Step 5: Display Results ──
    st.markdown("---")
    st.subheader("📊 Analysis Results")

    # Top metrics row
    m1, m2, m3, m4, m5 = st.columns(5)
    damage_score = prediction.get("damage_score", prediction.get("edge_density", 0))
    m1.metric("🎯 Severity",      report["severity"].upper())
    m2.metric("💰 Total Cost",    f"₹{report['total_cost']:,}")
    m3.metric("🔩 Parts Damaged", len(report["damaged_parts"]))
    m4.metric("📊 Confidence",    f"{report['confidence_score']}%")
    m5.metric("📈 Damage Score",  f"{damage_score:.3f}")

    st.markdown("---")

    # Zone damage scores visual bar
    zone_scores = prediction.get("zone_scores", {})
    if zone_scores:
        st.subheader("🗺️ Zone Damage Analysis")
        zcols = st.columns(4)
        zone_colors = {"no_damage": 0.0}
        labels = {"bumper": "🚗 Bumper", "headlight": "💡 Headlight",
                  "door": "🚪 Door", "windshield": "🪟 Windshield"}
        for i, part in enumerate(["bumper", "headlight", "door", "windshield"]):
            score = zone_scores.get(part, 0)
            with zcols[i]:
                st.markdown(f"**{labels[part]}**")
                st.progress(min(score / 0.4, 1.0))   # scale: 0.4 = max expected
                color = "🔴" if score > 0.28 else ("🟡" if score > 0.14 else ("🟠" if score > 0.06 else "🟢"))
                st.caption(f"{color} Score: {score:.3f}")

    st.markdown("---")

    # Two column layout: Damage details + Cost breakdown
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("🔧 Damage Assessment")

        # Severity badge
        severity_colors = {"no_damage": "✅", "minor": "🟢", "moderate": "🟡", "severe": "🔴"}
        sev = report["severity"]
        st.markdown(f"**Severity:** {severity_colors.get(sev, '⚪')} `{sev.upper()}`")

        st.markdown("**Damaged Parts Detected:**")
        if not report["damaged_parts"]:
            st.markdown("✅ No damaged parts detected")
        else:
            for part in report["damaged_parts"]:
                details = report["part_breakdown"].get(part, {})
                cost = details.get("cost", 0)
                st.markdown(f"- **{part.capitalize()}** → ₹{cost:,}" if cost else f"- **{part.capitalize()}**")

        # Confidence bar
        st.markdown(f"**Confidence Score:** {report['confidence_score']}%")
        st.progress(int(report['confidence_score']) / 100)

        # Claude/Ollama Vision description if available
        features = prediction.get("features", {})
        desc = features.get("description", "")
        visible = features.get("visible_parts", [])
        model_used = features.get("model_used", "")
        if desc:
            st.info(f"**👁️ AI sees:** {desc}")
        if visible:
            st.caption(f"Parts visible in photo: {', '.join(visible)}")

        # Analysis mode badge
        mode = report["analysis_mode"]
        if "OLLAMA" in mode:
            st.success(f"✅ {mode} — Local Vision AI")
        elif "CLAUDE" in mode:
            st.success(f"✅ {mode} — Vision AI")
        else:
            st.info(f"ℹ️ Analysis Mode: {mode}")

    with right_col:
        st.subheader("💰 Cost Breakdown")

        # Cost table
        cost_data = []
        for part, d in report["part_breakdown"].items():
            cost_data.append({
                "Part": part.capitalize(),
                "Severity": d['severity'],
                "Cost (₹)": f"₹{d['cost']:,}"
            })

        import pandas as pd
        df = pd.DataFrame(cost_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Totals
        st.markdown(f"""
        | | Amount |
        |---|---|
        | Parts Subtotal | ₹{report['subtotal_parts']:,} |
        | Labor (12%) | ₹{report['labor_cost']:,} |
        | GST (18%) | ₹{report['gst_amount']:,} |
        | **TOTAL** | **₹{report['total_cost']:,}** |
        """)

    # ── Decision Banner ──
    st.markdown("---")
    st.subheader("🏛️ Claim Decision")

    if report["decision"] == "NO_CLAIM":
        st.markdown(f"""
        <div class="decision-approved">
            ✅ NO DAMAGE DETECTED — NO CLAIM REQUIRED<br>
            {report['decision_reason']}
        </div>
        """, unsafe_allow_html=True)
    elif report["decision"] == "AUTO_APPROVED":
        st.markdown(f"""
        <div class="decision-approved">
            ✅ CLAIM AUTO-APPROVED<br>
            {report['decision_reason']}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="decision-review">
            ⚠️ MANUAL REVIEW REQUIRED<br>
            {report['decision_reason']}
        </div>
        """, unsafe_allow_html=True)

    # ── Business Logic Explanation ──
    with st.expander("📖 Business Logic Explanation"):
        st.markdown(f"""
        **How the decision was made:**

        1. **Image Analysis (CV_ANALYSIS mode):**
           - Edge Density: `{prediction.get('features', {}).get('edge_density', 0):.4f}`
           - Contrast Score: `{prediction.get('features', {}).get('contrast', 0):.4f}`
           - Dark Region Ratio: `{prediction.get('features', {}).get('dark_ratio', 0):.4f}`
           - Bright Spot Ratio: `{prediction.get('features', {}).get('bright_ratio', 0):.4f}`
           - **Composite Damage Score: `{prediction.get('damage_score', 0):.4f}`**

        2. **Severity Thresholds:**
           - Damage Score < 0.08 → Minor
           - Damage Score 0.08–0.18 → Moderate
           - Damage Score > 0.18 → **Severe**

        3. **Cost Calculation:**
           - Each damaged part's base cost × severity multiplier
           - Labor (15%) + GST (18%) added on top

        4. **Auto-Approval Criteria (both must be true):**
           - ✅ Total cost < ₹30,000 (Your total: ₹{report['total_cost']:,})
           - ✅ No severe damage (Severity: {report['severity']})

        5. **Final Decision: `{report['decision']}`**
           - {report['decision_reason']}
        """)

    # ── Raw JSON ──
    with st.expander("🔍 Raw ML Prediction JSON"):
        st.code(prediction_to_json(prediction), language="json")

    # ── Download Report ──
    st.markdown("---")
    st.subheader("📥 Download Report")

    text_report = generate_text_report(report)
    st.download_button(
        label="⬇️ Download Claim Report (.txt)",
        data=text_report,
        file_name=f"claim_report_{report['claim_id']}.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.caption(f"Claim ID: `{report['claim_id']}` | Generated: {report['timestamp']}")

else:
    # ── Empty State ──
    st.markdown("---")
    st.info("👆 Upload a vehicle damage image above to get started")

    # Demo preview
    with st.expander("🎬 What this app does"):
        st.markdown("""
        1. **Upload** a car damage photo (JPG/PNG)
        2. **OpenCV** preprocesses: resize → grayscale → blur → edge detection
        3. **ML Model** identifies damaged parts and classifies severity
        4. **Cost Engine** calculates repair costs with labor + GST
        5. **Business Logic** decides auto-approval or manual review
        6. **Download** a professional claim report
        """)