"""
Transaction Protection & Scam Detection Engine for Krishi AI.
Provides:
1. Tare & Weighbridge Discrepancy Auditing (Farmer Dispatch vs Buyer Receiving Slip)
2. Unauthorized Deduction & Price Deviation Detection
3. Payment Realization Verification (Agreed vs Received)
4. Formal APMC / Grievance Cell Dispute Filing
5. Objective Evidence-Based Risk Ratings (Never declares fraud without evidence)
"""
from typing import Dict, Any, List, Optional, Tuple

from modules.buyer_connect_db import (
    record_trade_transaction, get_transactions_for_user, file_transaction_dispute
)


def evaluate_transaction_risk(
    farmer_weight_kg: float,
    weighbridge_weight_kg: float,
    agreed_rate_per_kg: float,
    paid_rate_per_kg: float,
    deductions_amount: float = 0.0,
    payment_received: float = 0.0
) -> Dict[str, Any]:
    """
    Performs deterministic mathematical risk audit on agricultural transactions.
    """
    weight_diff_kg = farmer_weight_kg - weighbridge_weight_kg
    weight_diff_pct = (weight_diff_kg / farmer_weight_kg * 100.0) if farmer_weight_kg > 0 else 0.0
    expected_gross = farmer_weight_kg * agreed_rate_per_kg
    actual_gross = weighbridge_weight_kg * paid_rate_per_kg
    total_shortfall = max(0.0, (expected_gross - payment_received))

    rate_diff = agreed_rate_per_kg - paid_rate_per_kg

    flags = []
    risk_level = "LOW"
    badge_color = "#16834A"

    # 1. Weight Discrepancy Analysis
    if weight_diff_pct > 10.0:
        risk_level = "CRITICAL_DISCREPANCY"
        badge_color = "#DC2626"
        flags.append({
            "type": "SEVERE_WEIGHT_SHORTFALL",
            "severity": "Critical",
            "message": f"Weighbridge records {weight_diff_kg:.1f} kg ({weight_diff_pct:.1f}%) less than dispatch weight. Normal moisture loss for short hauls rarely exceeds 2–3%."
        })
    elif weight_diff_pct > 4.0:
        if risk_level != "CRITICAL_DISCREPANCY":
            risk_level = "MODERATE_DISCREPANCY"
            badge_color = "#D97706"
        flags.append({
            "type": "ELEVATED_WEIGHT_VARIANCE",
            "severity": "Warning",
            "message": f"Weight variance of {weight_diff_kg:.1f} kg ({weight_diff_pct:.1f}%) detected. Request certified weighbridge recalibration certificate."
        })

    # 2. Rate Deviation Analysis
    if rate_diff > 0.05:
        if risk_level != "CRITICAL_DISCREPANCY":
            risk_level = "MODERATE_DISCREPANCY"
            badge_color = "#D97706"
        flags.append({
            "type": "PRICE_DEVIATION",
            "severity": "Warning",
            "message": f"Settlement rate of ₹{paid_rate_per_kg:.2f}/kg is lower than contracted rate of ₹{agreed_rate_per_kg:.2f}/kg (deficit: ₹{rate_diff:.2f}/kg)."
        })

    # 3. Deductions Audit
    if deductions_amount > expected_gross * 0.05:
        risk_level = "CRITICAL_DISCREPANCY"
        badge_color = "#DC2626"
        flags.append({
            "type": "EXCESSIVE_DEDUCTIONS",
            "severity": "Critical",
            "message": f"Deductions of ₹{deductions_amount:,.2f} exceed 5% of gross invoice value without documented physical damage proof."
        })

    # 4. Payment Realization Audit
    if payment_received < (actual_gross - deductions_amount) * 0.90:
        risk_level = "CRITICAL_DISCREPANCY"
        badge_color = "#DC2626"
        flags.append({
            "type": "PAYMENT_UNDERSETTLEMENT",
            "severity": "Critical",
            "message": f"Actual funds received (₹{payment_received:,.2f}) leave an unpaid balance of ₹{(actual_gross - deductions_amount - payment_received):,.2f}."
        })

    if not flags:
        flags.append({
            "type": "CLEAN_AUDIT",
            "severity": "Info",
            "message": "Weights, prices, deductions, and payment receipts match contracted parameters within standard APMC operational tolerances."
        })

    return {
        "farmer_weight_kg": farmer_weight_kg,
        "weighbridge_weight_kg": weighbridge_weight_kg,
        "weight_diff_kg": weight_diff_kg,
        "weight_diff_pct": round(weight_diff_pct, 1),
        "expected_gross_rs": round(expected_gross, 2),
        "actual_gross_rs": round(actual_gross, 2),
        "total_shortfall_rs": round(total_shortfall, 2),
        "deductions_rs": round(deductions_amount, 2),
        "payment_received_rs": round(payment_received, 2),
        "risk_level": risk_level,
        "badge_color": badge_color,
        "flags": flags,
        "dispute_recommended": risk_level in ["CRITICAL_DISCREPANCY", "MODERATE_DISCREPANCY"]
    }
