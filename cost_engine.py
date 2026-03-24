# src/cost_engine.py
# Cost estimation engine — realistic Indian motor insurance repair costs.
from datetime import datetime

# ── Realistic repair costs (INR) ──
# Minor = surface scratch/dent, Moderate = panel work, Severe = replacement
PART_COSTS = {
    "bumper": {
        "minor":    3500,   # scratch/scuff repair
        "moderate": 8000,   # dent + repaint
        "severe":   18000,  # full replacement
    },
    "headlight": {
        "minor":    2000,   # lens polish / small crack
        "moderate": 5500,   # assembly repair
        "severe":   12000,  # full replacement
    },
    "windshield": {
        "minor": 2500,
        "moderate": 10000,
        "severe": 25000,   # upgraded
    },
    "door": {
        "minor": 4000,
        "moderate": 15000,
        "severe": 30000,   # upgraded
    },
}

LABOR_RATE = 0.12   # 12% of parts cost
GST_RATE   = 0.18   # 18% GST

AUTO_APPROVE_MAX  = 30000
AUTO_APPROVE_SEVERITY = {"minor", "moderate", "no_damage"}   # not severe


def estimate_cost(prediction: dict) -> dict:
    severity = prediction.get("severity", "minor")

    # No damage case
    if severity == "no_damage":
        return {
            "claim_id": f"MCE-{__import__('datetime').datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "damaged_parts": [],
            "severity": "no_damage",
            "part_breakdown": {},
            "subtotal_parts": 0,
            "labor_cost": 0,
            "gst_amount": 0,
            "total_cost": 0,
            "decision": "NO_CLAIM",
            "decision_reason": "No visible damage detected. Claim not required.",
            "confidence_score": prediction.get("confidence_score", 0),
            "edge_density": prediction.get("edge_density", 0),
            "damage_score": prediction.get("damage_score", 0),
            "analysis_mode": prediction.get("mode", "UNKNOWN"),
        }

    parts    = prediction.get("damaged_parts", [])
    severity = prediction.get("severity", "minor")

    part_breakdown = {}
    subtotal = 0

    for part in parts:
        cost = PART_COSTS.get(part, {}).get(severity, 5000)
        part_breakdown[part] = {"cost": cost, "severity": severity}
        subtotal += cost

    labor   = round(subtotal * LABOR_RATE)
    taxable = subtotal + labor
    gst     = round(taxable * GST_RATE)
    total   = taxable + gst

    # Business logic
    has_severe  = (severity == "severe")
    under_limit = (total < AUTO_APPROVE_MAX)

    if under_limit and not has_severe:
        decision = "AUTO_APPROVED"
        reason   = (
            f"Total ₹{total:,} is under ₹{AUTO_APPROVE_MAX:,} "
            f"and damage is {severity} → Auto-approved."
        )
    elif has_severe:
        decision = "MANUAL_REVIEW"
        reason   = "Severe damage detected → Requires assessor inspection."
    else:
        decision = "MANUAL_REVIEW"
        reason   = (
            f"Total ₹{total:,} exceeds ₹{AUTO_APPROVE_MAX:,} limit → Manual approval needed."
        )

    return {
        "claim_id":       f"MCE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "timestamp":      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "damaged_parts":  parts,
        "severity":       severity,
        "part_breakdown": part_breakdown,
        "subtotal_parts": subtotal,
        "labor_cost":     labor,
        "gst_amount":     gst,
        "total_cost":     total,
        "decision":       decision,
        "decision_reason":reason,
        "confidence_score": prediction.get("confidence_score", 0),
        "edge_density":   prediction.get("edge_density", 0),
        "damage_score":   prediction.get("damage_score", 0),
        "analysis_mode":  prediction.get("mode", "UNKNOWN"),
    }


def generate_text_report(report: dict) -> str:
    lines = [
        "=" * 58,
        "    INSTANT MOTOR CLAIM ESTIMATOR — CLAIM REPORT",
        "=" * 58,
        f"Claim ID    : {report['claim_id']}",
        f"Date & Time : {report['timestamp']}",
        f"Analysis    : {report['analysis_mode']}",
        f"Confidence  : {report['confidence_score']}%",
        "",
        "── DAMAGE ASSESSMENT ───────────────────────────────",
        f"Severity     : {report['severity'].upper()}",
        f"Damage Score : {report['damage_score']:.4f}",
        f"Damaged Parts: {', '.join(report['damaged_parts'])}",
        "",
        "── COST BREAKDOWN ──────────────────────────────────",
    ]

    for part, d in report["part_breakdown"].items():
        lines.append(f"  {part.capitalize():<12}: ₹{d['cost']:>7,}  ({d['severity']})")

    lines += [
        f"  {'Parts Total':<12}: ₹{report['subtotal_parts']:>7,}",
        f"  {'Labor (12%)':<12}: ₹{report['labor_cost']:>7,}",
        f"  {'GST (18%)':<12}: ₹{report['gst_amount']:>7,}",
        "-" * 40,
        f"  {'TOTAL':<12}: ₹{report['total_cost']:>7,}",
        "",
        "── DECISION ────────────────────────────────────────",
        f"  *** {report['decision']} ***",
        f"  {report['decision_reason']}",
        "",
        "=" * 58,
        "  Auto-generated report. Subject to physical verification.",
        "=" * 58,
    ]
    return "\n".join(lines)
