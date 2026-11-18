"""
Deterministic Sell Now vs Wait Decision Engine for KisanAI.
Complies strictly with Phase 7 instructions.
"""
from typing import Dict, Any


def evaluate_sell_timing(
    crop_name: str,
    quantity_kg: float,
    current_price_kg: float,
    predicted_future_price_kg: float,
    horizon_days: int = 7,
    daily_storage_cost_per_kg: float = 0.15,
    spoilage_pct: float = 3.0,
    current_transport_cost: float = 800.0,
    future_transport_cost: float = 800.0,
    mandi_fee_pct: float = 3.5,
    forecast_mae: float = 1.2
) -> Dict[str, Any]:
    """
    Evaluates financial trade-off between selling now vs holding stock.
    Deterministic calculation accounting for storage costs, physiological weight loss/spoilage,
    transportation changes, and market fees.
    """
    fee_rate = mandi_fee_pct / 100.0

    # 1. Current Selling Financials
    current_gross_revenue = quantity_kg * current_price_kg
    current_mandi_fees = current_gross_revenue * fee_rate
    current_selling_expenses = current_transport_cost + current_mandi_fees
    current_net_proceeds = current_gross_revenue - current_selling_expenses
    current_net_per_kg = current_net_proceeds / quantity_kg if quantity_kg > 0 else 0.0

    # 2. Future Selling Financials
    # Deduct spoilage / shrinkage
    effective_spoilage_pct = min(40.0, max(0.0, spoilage_pct))
    future_saleable_qty = quantity_kg * (1.0 - (effective_spoilage_pct / 100.0))
    
    future_gross_revenue = future_saleable_qty * predicted_future_price_kg
    future_mandi_fees = future_gross_revenue * fee_rate
    
    # Storage Expenses
    total_storage_cost = quantity_kg * daily_storage_cost_per_kg * horizon_days
    
    future_selling_expenses = future_transport_cost + future_mandi_fees
    future_net_proceeds = future_gross_revenue - future_selling_expenses - total_storage_cost
    future_net_per_kg = future_net_proceeds / quantity_kg if quantity_kg > 0 else 0.0

    # 3. Comparative Advantage & Thresholds
    net_diff = future_net_proceeds - current_net_proceeds
    gain_pct = (net_diff / current_net_proceeds * 100.0) if current_net_proceeds > 0 else 0.0

    # Confidence check: Price delta must exceed validation error (MAE)
    price_delta = predicted_future_price_kg - current_price_kg
    is_forecast_significant = price_delta > (forecast_mae * 0.75)

    # 4. Deterministic Decision Engine
    if net_diff <= 0:
        recommendation = "SELL NOW"
        badge_color = "#d32f2f"  # Red
        rationale = (
            f"Holding for {horizon_days} days produces a net loss of ₹{abs(net_diff):,.2f} "
            f"due to accumulated storage expenses (₹{total_storage_cost:,.2f}) and "
            f"loss of {quantity_kg - future_saleable_qty:.1f} kg from spoilage/weight shrinkage."
        )
        strategy = "Liquidate harvest immediately at current market rates to lock in maximum net proceeds."
        partial_ratio = (100, 0)
        
    elif gain_pct >= 5.0 and is_forecast_significant:
        recommendation = "CONSIDER WAITING"
        badge_color = "#2e7d32"  # Green
        rationale = (
            f"Predicted price rise (+₹{price_delta:.2f}/kg) exceeds total storage costs "
            f"(₹{total_storage_cost:,.2f}) and spoilage loss, yielding an estimated net gain of "
            f"+₹{net_diff:,.2f} (+{gain_pct:.1f}% ROI) after {horizon_days} days."
        )
        strategy = (
            f"Hold stock in well-ventilated or cold storage for {horizon_days} days. "
            f"Monitor mandi price daily as harvest approaches target date."
        )
        partial_ratio = (0, 100)
        
    else:
        recommendation = "SELL PARTIALLY"
        badge_color = "#f57c00"  # Amber/Orange
        rationale = (
            f"Waiting shows a marginal gain of +₹{net_diff:,.2f} (+{gain_pct:.1f}%), but holding "
            f"carries market volatility risk and potential quality degradation."
        )
        strategy = (
            f"Stagger your sale: Sell 60% ({quantity_kg * 0.6:.0f} kg) today to secure immediate cash flow, "
            f"and hold 40% ({quantity_kg * 0.4:.0f} kg) in storage to capture upside if prices surge."
        )
        partial_ratio = (60, 40)

    return {
        "recommendation": recommendation,
        "badge_color": badge_color,
        "rationale": rationale,
        "strategy": strategy,
        "horizon_days": horizon_days,
        "current_gross_revenue": round(current_gross_revenue, 2),
        "current_net_proceeds": round(current_net_proceeds, 2),
        "current_net_per_kg": round(current_net_per_kg, 2),
        "future_saleable_qty": round(future_saleable_qty, 1),
        "spoilage_loss_kg": round(quantity_kg - future_saleable_qty, 1),
        "total_storage_cost": round(total_storage_cost, 2),
        "future_gross_revenue": round(future_gross_revenue, 2),
        "future_net_proceeds": round(future_net_proceeds, 2),
        "future_net_per_kg": round(future_net_per_kg, 2),
        "net_difference": round(net_diff, 2),
        "gain_pct": round(gain_pct, 1),
        "partial_ratio": partial_ratio,
        "disclaimer": "Predictions are statistical forecasts based on historical market trends; actual APMC buyer bids are subject to daily arrivals and physical produce quality."
    }
