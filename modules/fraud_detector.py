"""
Suspicious Buyer Offer & Unfair Transaction Detector for KisanAI.
Complies with Objective 7: detects predatory bids, unfair middleman practices,
calculates farmer loss, and generates actionable counter-negotiation scripts.
"""
from typing import Dict, Any, List


def evaluate_buyer_offer(
    offered_price_kg: float,
    quantity_kg: float,
    benchmark_modal_price_kg: float,
    best_mandi_net_price_kg: float,
    payment_terms: str = "Immediate Cash / UPI",
    quality_score: float = 85.0
) -> Dict[str, Any]:
    """
    Evaluates buyer offer against fair market price band and farmgate net parity.
    """
    # Farmgate parity benchmark is what farmer would net at best nearby mandi
    benchmark_parity = max(best_mandi_net_price_kg, benchmark_modal_price_kg * 0.88)
    
    # Calculate price delta
    price_delta = offered_price_kg - benchmark_parity
    delta_pct = (price_delta / benchmark_parity * 100.0) if benchmark_parity > 0 else 0.0

    total_offered_proceeds = offered_price_kg * quantity_kg
    total_fair_proceeds = benchmark_parity * quantity_kg
    farmer_loss_gain = total_offered_proceeds - total_fair_proceeds

    # Unfairness & Predatory Classification
    if delta_pct < -20.0:
        status = "PREDATORY OFFER (HIGH RISK)"
        badge_color = "#b71c1c"  # Dark Red
        alert_type = "error"
        summary = (
            f"The offered price of ₹{offered_price_kg:.2f}/kg is {abs(delta_pct):.1f}% BELOW fair market parity! "
            f"Accepting this offer causes an immediate loss of ₹{abs(farmer_loss_gain):,.2f} for your {quantity_kg:.0f} kg crop."
        )
    elif delta_pct < -8.0:
        status = "BELOW FAIR MARKET VALUE"
        badge_color = "#e65100"  # Amber Orange
        alert_type = "warning"
        summary = (
            f"The offer of ₹{offered_price_kg:.2f}/kg is {abs(delta_pct):.1f}% below wholesale mandi net rates. "
            f"You stand to lose ₹{abs(farmer_loss_gain):,.2f} compared to direct mandi dispatch."
        )
    elif delta_pct <= 5.0:
        status = "FAIR & COMPETITIVE OFFER"
        badge_color = "#2e7d32"  # Green
        alert_type = "success"
        summary = (
            f"The offer of ₹{offered_price_kg:.2f}/kg is fair and aligns closely with mandi net returns "
            f"after accounting for transport savings and zero mandi cess."
        )
    else:
        status = "PREMIUM OFFER (ATTRACTIVE)"
        badge_color = "#1565c0"  # Blue
        alert_type = "info"
        summary = (
            f"The offer of ₹{offered_price_kg:.2f}/kg is {delta_pct:.1f}% ABOVE typical wholesale net returns! "
            f"Verify buyer payment credentials and execute the trade promptly."
        )

    # Risk Flags
    risk_flags = []
    if "credit" in payment_terms.lower() or "15 days" in payment_terms.lower() or "unspecified" in payment_terms.lower():
        risk_flags.append("⚠️ Deferred Credit Risk: Delayed payments in informal trade carry 30%+ default or renegotiation rate.")
    if delta_pct < -15.0:
        risk_flags.append("⚠️ Middleman Arbitrage: Buyer is likely purchasing at a steep discount to resell at regional APMC.")
    if quality_score >= 80.0 and offered_price_kg < benchmark_modal_price_kg:
        risk_flags.append("⚠️ Quality Undervaluation: Your produce has Grade A/FAQ quality score, but is being priced as substandard.")

    # Counter-offer recommendation
    recommended_counter_kg = round(max(offered_price_kg, benchmark_parity * 1.02), 2)
    counter_total_proceeds = recommended_counter_kg * quantity_kg
    extra_money = counter_total_proceeds - total_offered_proceeds

    # Negotiation Dialogue Script
    negotiation_script = (
        f"\"Namaste Ji, I have tested market arrivals today. In nearby APMC mandis, "
        f"FAQ tomato is trading at ₹{benchmark_modal_price_kg:.2f}/kg, giving me ₹{benchmark_parity:.2f}/kg "
        f"net in hand even after paying transport and cess. My produce is sorted with a high quality score of {quality_score:.0f}/100. "
        f"I cannot accept ₹{offered_price_kg:.2f}/kg. My bottom price for immediate loading is ₹{recommended_counter_kg:.2f}/kg.\""
    )

    return {
        "status": status,
        "badge_color": badge_color,
        "alert_type": alert_type,
        "offered_price_kg": round(offered_price_kg, 2),
        "benchmark_parity_kg": round(benchmark_parity, 2),
        "benchmark_modal_price_kg": round(benchmark_modal_price_kg, 2),
        "price_delta": round(price_delta, 2),
        "delta_pct": round(delta_pct, 1),
        "total_offered_proceeds": round(total_offered_proceeds, 2),
        "total_fair_proceeds": round(total_fair_proceeds, 2),
        "farmer_loss_gain": round(farmer_loss_gain, 2),
        "summary": summary,
        "risk_flags": risk_flags,
        "recommended_counter_kg": recommended_counter_kg,
        "counter_total_proceeds": round(counter_total_proceeds, 2),
        "extra_money_from_counter": round(extra_money, 2),
        "negotiation_script": negotiation_script
    }
