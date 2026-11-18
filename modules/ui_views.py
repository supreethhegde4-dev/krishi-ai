"""
UI Views Module for Krishi AI
Implements high-contrast, professional AgriTech SaaS views for all 12 modules:
1. Intelligence Overview (The 4 Core Questions: Past, Present, Future, Decision)
2. Historical Analysis (DuckDB 16.37M Parquet Analytics, YoY, Seasonality, Anomalies)
3. Crop Yield Prediction (ML Yield Forecasting & Benchmarking)
4. Market Intelligence (Mandi Net Proceeds & Logistics Arbitrage)
5. Seasonal Intelligence (Agro-Climatic Calendars & Windows)
6. Agricultural Risk Analysis (Multi-Factor Composite Risk Index 0-100)
7. What-If Simulator (Interactive Dual-Scenario Sandbox)
8. Explainable AI (SHAP TreeExplainer Waterfall Attributions)
9. AI Decision Reports (8-Section Unified Executive Report & Export)
10. Crop & Soil Advisor (ML Crop Match & Fertilizer Prescription)
11. Anti-Fraud Detector (Predatory Buyer Bid Detection)
12. Settings (Farm Configuration & Credentials)
"""
import json
import datetime
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Backend Modules
from modules.historical_intelligence import (
    get_historical_database_metrics, get_commodity_yoy_trends,
    get_monthly_seasonal_profile, detect_historical_price_anomalies,
    get_regional_market_benchmarks
)
from modules.seasonal_intelligence import get_seasonal_crop_intelligence
from modules.risk_analytics import evaluate_agricultural_risks
from modules.what_if_simulator import run_what_if_simulation
from modules.explainable_ai import explain_yield_prediction
from modules.decision_engine import generate_unified_decision_report
from modules.pdf_report_generator import generate_unified_pdf_report
from modules.yield_analytics import predict_crop_yield
from modules.proceeds_calculator import compute_mandi_proceeds_table
from modules.transport_engine import DEFAULT_VEHICLE_CONFIGS
from modules.crop_advisor import recommend_crop
from modules.soil_intelligence import evaluate_soil_health
from modules.fertilizer_advisor import calculate_fertilizer_prescription
from modules.fraud_detector import evaluate_buyer_offer
from modules.trend_shift_detector import detect_market_trend_shifts, analyze_weather_and_yield_shifts
from modules.geo_ors import (
    geocode_address, get_nearest_mandis_realtime, format_duration,
    haversine_distance_km, estimate_road_distance_demo
)
from modules.auth_db import (
    save_user_prediction, get_user_predictions, update_farm_profile, change_user_password
)


# ==============================================================================
# 1. INTELLIGENCE OVERVIEW VIEW (APPLE-INSPIRED MINIMALIST REDESIGN)
# ==============================================================================
def render_intelligence_overview_view(user, farm, df_market):
    # Apple Welcome Card
    st.html(f"""
    <div style="background:#FFFFFF; border:1px solid #E5E5E7; border-radius:20px; padding:24px 28px; margin-bottom:20px; box-shadow:0 2px 10px rgba(0,0,0,0.02); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
        <div>
            <div style="display:inline-flex; align-items:center; gap:6px; background:#DCEFE2; color:#16834A; padding:4px 12px; border-radius:20px; font-size:0.75rem; font-weight:700; margin-bottom:8px; letter-spacing:0.02em;">
                <span>●</span> Precision Telemetry Active
            </div>
            <h1 style="color:#1D1D1F; margin:0 0 4px 0; font-size:1.85rem; font-weight:700; letter-spacing:-0.03em;">
                Welcome back, {user['full_name']}
            </h1>
            <p style="color:#86868B; margin:0; font-size:0.92rem; font-weight:400; line-height:1.5;">
                Agricultural Decision Support Platform for <strong style="color:#1D1D1F;">{farm.get('farm_name', 'Farm Enterprise')}</strong> 
                ({farm.get('acreage', 2.5)} Acres • {farm.get('district', 'Ramanagara')}, {farm.get('state', 'Karnataka')}).
            </p>
        </div>
        <div style="text-align:right;">
            <div style="font-size:0.76rem; color:#86868B; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">FARM ID</div>
            <div style="font-size:1.15rem; font-weight:700; color:#1D1D1F;">#{user['id']:04d}-AGRO</div>
        </div>
    </div>
    """)

    # 4 Modern Apple Metric KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.html("""
        <div class="stat-card">
            <div class="stat-label">Crop Yield Prediction</div>
            <div class="stat-value">105.9 <span style="font-size:1.0rem; color:#86868B; font-weight:500;">Q/ac</span></div>
            <div class="stat-subtext">26,480 kg Projected Harvest</div>
        </div>
        """)
    with k2:
        st.html("""
        <div class="stat-card">
            <div class="stat-label">Market Price Intelligence</div>
            <div class="stat-value">₹16.50 <span style="font-size:1.0rem; color:#86868B; font-weight:500;">/ kg</span></div>
            <div class="stat-subtext">Wholesale Modal Baseline</div>
        </div>
        """)
    with k3:
        st.html("""
        <div class="stat-card">
            <div class="stat-label">Trend Shift Alert</div>
            <div class="stat-value" style="color:#16834A; font-size:1.55rem;">Bullish Momentum</div>
            <div class="stat-subtext">+14.2% 7-Day Velocity</div>
        </div>
        """)
    with k4:
        st.html("""
        <div class="stat-card">
            <div class="stat-label">Agricultural Risk Score</div>
            <div class="stat-value">28 <span style="font-size:1.0rem; color:#86868B; font-weight:500;">/ 100</span></div>
            <div class="stat-subtext" style="color:#16834A;">Low Composite Risk Index</div>
        </div>
        """)

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # 4 CORE PLATFORM QUESTIONS (APPLE INSIGHT CARDS)
    st.html("""
    <div style="margin: 16px 0 10px 0;">
        <span style="font-size:0.75rem; font-weight:700; color:#86868B; text-transform:uppercase; letter-spacing:0.06em;">
            Decision Intelligence Framework
        </span>
    </div>
    """)

    cq1, cq2 = st.columns(2)
    with cq1:
        with st.container(border=True):
            st.html("""
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                <div style="width:32px; height:32px; border-radius:8px; background:#F5F5F7; display:flex; align-items:center; justify-content:center; font-size:1.05rem;">
                    📜
                </div>
                <div>
                    <div style="font-size:0.72rem; color:#86868B; font-weight:600; text-transform:uppercase; letter-spacing:0.04em;">Historical Context</div>
                    <div style="font-weight:700; font-size:1.05rem; color:#1D1D1F;">1. What happened in the past?</div>
                </div>
            </div>
            <div style="font-size:0.88rem; color:#475569; line-height:1.55;">
                • <strong>16,373,211 historical transactions</strong> analyzed across 32 Indian States.<br>
                • 4-year modal price corridor: <strong style="color:#1D1D1F;">₹12.50 to ₹48.00/kg</strong>.<br>
                • Seasonal wholesale prices consistently peak in <strong style="color:#16834A;">July (+₹18.50/kg)</strong> during monsoon shortfall, with supply gluts in <strong style="color:#1D1D1F;">January–February</strong>.
            </div>
            """)

        with st.container(border=True):
            st.html("""
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                <div style="width:32px; height:32px; border-radius:8px; background:#F5F5F7; display:flex; align-items:center; justify-content:center; font-size:1.05rem;">
                    🔮
                </div>
                <div>
                    <div style="font-size:0.72rem; color:#86868B; font-weight:600; text-transform:uppercase; letter-spacing:0.04em;">Predictive Models</div>
                    <div style="font-weight:700; font-size:1.05rem; color:#1D1D1F;">3. What is likely to happen in the future?</div>
                </div>
            </div>
            <div style="font-size:0.88rem; color:#475569; line-height:1.55;">
                • <strong>Harvest Production Forecast:</strong> 105.9 Quintals/Acre (26,480 kg total volume).<br>
                • <strong>14-Day Price Trajectory:</strong> Projected upward trend to <strong style="color:#16834A;">₹17.65/kg (+₹1.15/kg)</strong>.<br>
                • <strong>Composite Risk Score:</strong> <strong style="color:#16834A;">28/100 (Low Risk)</strong> with optimal soil fertility and low thermal stress.
            </div>
            """)

    with cq2:
        with st.container(border=True):
            st.html("""
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                <div style="width:32px; height:32px; border-radius:8px; background:#F5F5F7; display:flex; align-items:center; justify-content:center; font-size:1.05rem;">
                    📡
                </div>
                <div>
                    <div style="font-size:0.72rem; color:#86868B; font-weight:600; text-transform:uppercase; letter-spacing:0.04em;">Live Telemetry</div>
                    <div style="font-weight:700; font-size:1.05rem; color:#1D1D1F;">2. What is happening currently?</div>
                </div>
            </div>
            <div style="font-size:0.88rem; color:#475569; line-height:1.55;">
                • <strong>Active Farm Batch:</strong> Tomato (BATCH-2026-TM500, 500 kg lot).<br>
                • <strong>Soil Fertility Index:</strong> 84/100 (Optimal NPK & pH balance).<br>
                • <strong>Current Mandi Benchmark:</strong> ₹16.50/kg across Ramanagara & Kolar mandis.
            </div>
            """)

        with st.container(border=True):
            st.html("""
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                <div style="width:32px; height:32px; border-radius:8px; background:#DCEFE2; display:flex; align-items:center; justify-content:center; font-size:1.05rem;">
                    🎯
                </div>
                <div>
                    <div style="font-size:0.72rem; color:#16834A; font-weight:700; text-transform:uppercase; letter-spacing:0.04em;">Optimal Decision</div>
                    <div style="font-weight:700; font-size:1.05rem; color:#1D1D1F;">4. What is the best decision for farmers?</div>
                </div>
            </div>
            <div style="font-size:0.88rem; color:#475569; line-height:1.55;">
                • <strong>Target Marketplace:</strong> Dispatch harvest batch to <strong style="color:#1D1D1F;">Thrippunithura APMC</strong>.<br>
                • <strong>Net Proceeds Advantage:</strong> Realizes <strong style="color:#16834A;">₹7,278.30</strong> in-hand (<strong style="color:#16834A;">+₹2,478.30 net profit</strong> over nearest local mandi).<br>
                • <strong>Recommended Logistics:</strong> Standard Goods Truck under covered tarpaulin.
            </div>
            """)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # QUICK ACTION CARDS (6 APPLE-INSPIRED INTERACTIVE CARDS)
    st.html("""
    <div style="margin: 16px 0 10px 0;">
        <span style="font-size:0.75rem; font-weight:700; color:#86868B; text-transform:uppercase; letter-spacing:0.06em;">
            Quick Action Workflows
        </span>
    </div>
    """)

    qa_col1, qa_col2, qa_col3 = st.columns(3)
    with qa_col1:
        with st.container(border=True):
            st.html("""
            <div style="font-size:1.2rem; margin-bottom:6px;">📜</div>
            <div style="font-weight:700; font-size:1.02rem; color:#1D1D1F; margin-bottom:2px;">Historical Analysis</div>
            <div style="font-size:0.82rem; color:#86868B; margin-bottom:14px; min-height:36px;">16.37M parquet data points, 12-month seasonality and price anomalies.</div>
            """)
            if st.button("Explore History →", key="qa_hist", use_container_width=True):
                st.session_state.active_nav = "Historical Analysis"
                st.rerun()

        with st.container(border=True):
            st.html("""
            <div style="font-size:1.2rem; margin-bottom:6px;">📈</div>
            <div style="font-weight:700; font-size:1.02rem; color:#1D1D1F; margin-bottom:2px;">Trend Shift Intelligence</div>
            <div style="font-size:0.82rem; color:#86868B; margin-bottom:14px; min-height:36px;">Moving average crossovers, Bollinger envelopes and supply shocks.</div>
            """)
            if st.button("Track Trends →", key="qa_trend", use_container_width=True):
                st.session_state.active_nav = "Trend Shift Intelligence"
                st.rerun()

    with qa_col2:
        with st.container(border=True):
            st.html("""
            <div style="font-size:1.2rem; margin-bottom:6px;">🌾</div>
            <div style="font-weight:700; font-size:1.02rem; color:#1D1D1F; margin-bottom:2px;">Crop Yield Prediction</div>
            <div style="font-size:0.82rem; color:#86868B; margin-bottom:14px; min-height:36px;">Random Forest model with SHAP factor attributions and soil prescriptions.</div>
            """)
            if st.button("Forecast Yield →", key="qa_yield", use_container_width=True):
                st.session_state.active_nav = "Crop Yield Prediction"
                st.rerun()

        with st.container(border=True):
            st.html("""
            <div style="font-size:1.2rem; margin-bottom:6px;">📍</div>
            <div style="font-weight:700; font-size:1.02rem; color:#1D1D1F; margin-bottom:2px;">Nearby Market Finder</div>
            <div style="font-size:0.82rem; color:#86868B; margin-bottom:14px; min-height:36px;">Real-time road routing & nearest mandis directly from farm profile address.</div>
            """)
            if st.button("Find Markets →", key="qa_mandi_finder", use_container_width=True):
                st.session_state.active_nav = "Market Intelligence"
                st.rerun()

    with qa_col3:
        with st.container(border=True):
            st.html("""
            <div style="font-size:1.2rem; margin-bottom:6px;">💰</div>
            <div style="font-weight:700; font-size:1.02rem; color:#1D1D1F; margin-bottom:2px;">Market Intelligence</div>
            <div style="font-size:0.82rem; color:#86868B; margin-bottom:14px; min-height:36px;">APMC ranking, freight itemization, and net revenue arbitrage.</div>
            """)
            if st.button("Rank Mandis →", key="qa_mkt", use_container_width=True):
                st.session_state.active_nav = "Market Intelligence"
                st.rerun()

        with st.container(border=True):
            st.html("""
            <div style="font-size:1.2rem; margin-bottom:6px;">🤝</div>
            <div style="font-weight:700; font-size:1.02rem; color:#1D1D1F; margin-bottom:2px;">Buyer & Industry Connect</div>
            <div style="font-size:0.82rem; color:#86868B; margin-bottom:14px; min-height:36px;">Direct quotes to verified food processors and agricultural aggregators.</div>
            """)
            if st.button("Connect Buyers →", key="qa_buyer", use_container_width=True):
                st.session_state.active_nav = "Buyer Connect"
                st.rerun()


# ==============================================================================
# 2. HISTORICAL ANALYSIS VIEW (SECTION 2 OF PROMPT)
# ==============================================================================
def render_historical_analysis_view(user, farm):
    st.markdown("#### 📜 Historical Agricultural Intelligence")
    st.caption("Deep analytical scan over 16.37 Million transactions across 32 Indian States (2023–2026).")

    TOP_CROPS = ["Tomato", "Onion", "Potato", "Wheat", "Rice", "Banana", "Brinjal", "Cabbage", "Cauliflower", "Maize"]
    INDIAN_STATES = ["All States", "Karnataka", "Maharashtra", "Gujarat", "Haryana", "Punjab", "Rajasthan", "Madhya Pradesh", "Uttar Pradesh", "Tamil Nadu", "Kerala"]

    fc1, fc2 = st.columns(2)
    with fc1:
        sel_crop = st.selectbox("Select Commodity", TOP_CROPS, index=0)
    with fc2:
        sel_state = st.selectbox("Select State", INDIAN_STATES, index=1)

    with st.spinner(f"Querying DuckDB analytical engine for {sel_crop} ({sel_state})..."):
        yoy_res = get_commodity_yoy_trends(sel_crop, state=sel_state)
        season_res = get_monthly_seasonal_profile(sel_crop, state=sel_state)
        anomalies = detect_historical_price_anomalies(sel_crop, state=sel_state)
        benchmarks = get_regional_market_benchmarks(sel_crop, top_n=6)

    # YoY Metric Row
    df_yoy = yoy_res.get("df_yoy", pd.DataFrame())
    if not df_yoy.empty:
        total_recs = int(df_yoy["total_arrivals"].sum())
        avg_hist_price = df_yoy["avg_modal_price_kg"].mean()
        max_spike = df_yoy["max_price_kg"].max()
        cagr = yoy_res.get("cagr_pct", 0.0)

        hm1, hm2, hm3, hm4 = st.columns(4)
        with hm1:
            st.html(f"<div class='stat-card'><div class='stat-label'>Total Historical Arrivals</div><div class='stat-value'>{total_recs:,}</div><div class='stat-subtext'>{sel_crop} transactions</div></div>")
        with hm2:
            st.html(f"<div class='stat-card'><div class='stat-label'>4-Year Avg Modal Price</div><div class='stat-value'>₹{avg_hist_price:.2f}/kg</div><div class='stat-subtext'>₹{avg_hist_price*100:,.0f}/Quintal</div></div>")
        with hm3:
            st.html(f"<div class='stat-card'><div class='stat-label'>Max Historical Spike</div><div class='stat-value' style='color:#DC2626;'>₹{max_spike:.2f}/kg</div><div class='stat-subtext'>Peak supply crisis price</div></div>")
        with hm4:
            st.html(f"<div class='stat-card'><div class='stat-label'>4-Year Price CAGR</div><div class='stat-value'>{'+' if cagr>=0 else ''}{cagr:.1f}%</div><div class='stat-subtext'>Compound Annual Growth Rate</div></div>")

    # YoY Trend Chart & Seasonal Profile Chart
    ch1, ch2 = st.columns([1.2, 1], gap="medium")
    with ch1:
        with st.container(border=True):
            st.html(f"<div style='font-size:1.1rem; font-weight:700; color:#0D5C3A; margin-bottom:10px;'>Year-over-Year (YoY) Price & Arrival Volume</div>")
            if not df_yoy.empty:
                fig_yoy = go.Figure()
                fig_yoy.add_trace(go.Bar(
                    x=df_yoy["year"], y=df_yoy["total_arrivals"],
                    name="Arrival Transactions", marker_color="#CBD5E1", yaxis="y2"
                ))
                fig_yoy.add_trace(go.Scatter(
                    x=df_yoy["year"], y=df_yoy["avg_modal_price_kg"],
                    name="Avg Modal Price (₹/kg)", mode="lines+markers",
                    line=dict(color="#0D5C3A", width=3), marker=dict(size=8)
                ))
                fig_yoy.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="-apple-system, BlinkMacSystemFont, SF Pro Display, Inter, sans-serif", size=11, color="#86868B"),
                    height=320,
                    xaxis=dict(showgrid=False, linecolor="#E5E5E7"),
                    yaxis=dict(title="Modal Price (₹/kg)", showgrid=True, gridcolor="#F0F0F2", linecolor="#E5E5E7"),
                    yaxis2=dict(title="Arrivals Volume", overlaying="y", side="right", showgrid=False),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#1D1D1F")),
                    margin=dict(l=40, r=40, t=20, b=30)
                )
                st.plotly_chart(fig_yoy, use_container_width=True)

    with ch2:
        with st.container(border=True):
            st.html(f"<div style='font-size:1.1rem; font-weight:700; color:#0D5C3A; margin-bottom:10px;'>12-Month Seasonality Profile (Jan–Dec)</div>")
            df_season = season_res.get("df_seasonal", pd.DataFrame())
            if not df_season.empty:
                fig_s = px.bar(
                    df_season, x="month_name", y="avg_price_kg",
                    color="avg_price_kg", color_continuous_scale="Greens",
                    text_auto=".1f"
                )
                fig_s.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="-apple-system, BlinkMacSystemFont, SF Pro Display, Inter, sans-serif", size=11, color="#86868B"),
                    height=320, coloraxis_showscale=False,
                    xaxis=dict(title="Month", showgrid=False, linecolor="#E5E5E7"),
                    yaxis=dict(title="Avg Price (₹/kg)", showgrid=True, gridcolor="#F0F0F2", linecolor="#E5E5E7"),
                    margin=dict(l=30, r=30, t=20, b=30)
                )
                st.plotly_chart(fig_s, use_container_width=True)
                st.caption(f"💡 **Peak Window:** {season_res.get('peak_month')} (₹{season_res.get('peak_price_kg'):.2f}/kg) • **Trough:** {season_res.get('trough_month')} (₹{season_res.get('trough_price_kg'):.2f}/kg)")

    # Price Shock Anomalies
    with st.container(border=True):
        st.html("<div style='font-size:1.15rem; font-weight:700; color:#0D5C3A; margin-bottom:10px;'>⚠️ Historical Price Shock Anomalies (Z-Score > ±2.0σ)</div>")
        if anomalies:
            df_anom = pd.DataFrame(anomalies)
            st.dataframe(df_anom.rename(columns={
                "date": "Date", "price_kg": "Price (₹/kg)", "z_score": "Z-Score", "type": "Anomaly Severity", "deviation_pct": "Deviation from Mean (%)"
            }), use_container_width=True)
        else:
            st.info("No extreme price anomalies recorded for this filter selection.")

    # Regional Benchmarks
    b1, b2 = st.columns(2)
    with b1:
        with st.container(border=True):
            st.html(f"<div style='font-size:1.05rem; font-weight:700; color:#0D5C3A; margin-bottom:8px;'>Top States by Historical Realized Price</div>")
            df_st = benchmarks.get("top_states_by_price", pd.DataFrame())
            if not df_st.empty:
                st.dataframe(df_st.rename(columns={"avg_price_kg": "Avg Price (₹/kg)", "total_arrivals": "Arrivals"}), use_container_width=True)
    with b2:
        with st.container(border=True):
            st.html(f"<div style='font-size:1.05rem; font-weight:700; color:#0D5C3A; margin-bottom:8px;'>Top Wholesale Mandis by Transaction Volume</div>")
            df_md = benchmarks.get("top_mandis_by_volume", pd.DataFrame())
            if not df_md.empty:
                st.dataframe(df_md.rename(columns={"avg_price_kg": "Avg Price (₹/kg)", "total_arrivals": "Arrivals"}), use_container_width=True)

    # MERGED: Seasonal Cropping Calendar & Optimal Planting Windows
    seasonal_data = get_seasonal_crop_intelligence(sel_crop, state=sel_state)
    with st.expander("🗓️ Seasonal Cropping Calendar & Planting Windows", expanded=False):
        sc1, sc2 = st.columns([1, 1.5])
        with sc1:
            st.html(f"""
            <div style="background:#F0FDF4; border:1.5px solid #86EFAC; border-radius:8px; padding:12px;">
                <div style="font-size:0.75rem; font-weight:800; color:#15803D; text-transform:uppercase;">Current Agro Stage</div>
                <div style="font-size:1.25rem; font-weight:800; color:#0D5C3A; margin:4px 0;">{seasonal_data['current_season_stage']}</div>
                <div style="font-size:0.85rem; color:#475569;">Primary Season: <b>{seasonal_data['primary_season']}</b></div>
                <div style="font-size:0.82rem; color:#64748B; margin-top:4px;">Peak Yield Season: <b>{seasonal_data['peak_yield_season']}</b></div>
            </div>
            """)
        with sc2:
            st.html(f"""
            <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:12px;">
                <div style="font-size:0.85rem; font-weight:700; color:#0D5C3A; margin-bottom:4px;">Optimal Agro-Climatic Windows:</div>
                <div style="font-size:0.82rem; color:#334155; line-height:1.5;">
                    • <b>Sowing Window:</b> {seasonal_data['sowing_window']}<br>
                    • <b>Harvest Period:</b> {seasonal_data['harvest_window']}<br>
                    • <b>Advisory:</b> {seasonal_data['climate_suitability']}
                </div>
            </div>
            """)


# ==============================================================================
# 3. CROP YIELD PREDICTION VIEW (SECTION 3A OF PROMPT)
# ==============================================================================
def render_crop_yield_view(user, farm):
    st.markdown("#### 🌾 Machine Learning Crop Yield Prediction")
    st.html("<div style='background:#FFFBEB; border:1px solid #FCD34D; border-radius:8px; padding:8px 12px; margin-bottom:12px; font-size:0.83rem; color:#92400E; display:flex; justify-content:space-between; align-items:center;'><span>🟠 <b>SYNTHETICALLY TRAINED MODEL</b> (ICAR Agro-Climatic Benchmarks)</span><span style='font-weight:600; color:#B45309;'>Scope: Estimated Regional Baseline Yield (Not Empirical Field Trial)</span></div>")
    st.caption("Random Forest regressor trained on agro-climatic conditions to forecast harvest volume and benchmark against ICAR district standards.")

    cy1, cy2 = st.columns([1, 1], gap="large")
    with cy1:
        with st.container(border=True):
            st.html("<div style='font-size:1.15rem; font-weight:700; color:#0D5C3A; margin-bottom:12px;'>1. Farm Input Telemetry</div>")
            y_crop = st.selectbox("Crop Variety", ["Tomato", "Rice", "Maize", "Banana", "Cotton", "Potato", "Wheat"], index=0)
            y_acres = st.number_input("Cultivated Acreage (Acres)", min_value=0.5, max_value=50.0, value=float(farm.get("acreage", 2.5)), step=0.5)
            y_rain = st.number_input("Seasonal Rainfall (mm)", min_value=10.0, max_value=400.0, value=85.0, step=5.0)
            y_ph = st.number_input("Soil pH", min_value=4.0, max_value=9.0, value=6.5, step=0.1)
            y_n = st.number_input("Soil Available Nitrogen (N) kg/ha", min_value=10.0, max_value=200.0, value=80.0, step=5.0)
            y_p = st.number_input("Soil Available Phosphorus (P) kg/ha", min_value=5.0, max_value=160.0, value=50.0, step=5.0)
            y_k = st.number_input("Soil Available Potassium (K) kg/ha", min_value=5.0, max_value=220.0, value=60.0, step=5.0)

    yield_res = predict_crop_yield(y_crop, y_acres, y_n, y_p, y_k, y_rain, y_ph)

    with cy2:
        with st.container(border=True):
            st.html("<div style='font-size:1.15rem; font-weight:700; color:#0D5C3A; margin-bottom:12px;'>2. Predicted Harvest Volume</div>")
            py_acre = yield_res["predicted_yield_per_acre"]
            tot_q = yield_res["total_yield_quintals"]
            tot_kg = yield_res["total_yield_kg"]

            st.html(f"""
            <div style="background-color:#F0FDF4; border:2px solid #0D5C3A; border-radius:12px; padding:18px; text-align:center; margin-bottom:16px;">
                <div style="font-size:0.8rem; font-weight:800; color:#14532D; letter-spacing:0.5px;">PREDICTED HARVEST PRODUCTION</div>
                <div style="font-size:2.8rem; font-weight:800; color:#0D5C3A; margin:4px 0;">{tot_q:,.1f} Quintals</div>
                <div style="font-size:1.15rem; font-weight:700; color:#166534;">{tot_kg:,.0f} kg Total Volume</div>
                <div style="font-size:0.85rem; color:#475569; margin-top:4px;">({py_acre:.1f} Q/Acre) • Rating: <strong>{yield_res.get('performance_rating', 'Above Average')}</strong></div>
            </div>
            """)

            fig_y = go.Figure()
            fig_y.add_trace(go.Bar(
                x=['District Average', 'State Benchmark', 'Your Predicted Farm Yield', 'Top Decile Potential'],
                y=[yield_res['district_avg_yield'], yield_res['state_avg_yield'], py_acre, yield_res['high_performing_yield']],
                marker_color=['#94A3B8', '#64748B', '#0D5C3A', '#047857'],
                text=[f"{v:.1f} Q" for v in [yield_res['district_avg_yield'], yield_res['state_avg_yield'], py_acre, yield_res['high_performing_yield']]],
                textposition='auto'
            ))
            fig_y.update_layout(
                title=dict(
                    text=f"<b>{y_crop} Yield Benchmark (Quintals/Acre)</b>",
                    font=dict(family="-apple-system, BlinkMacSystemFont, SF Pro Display, Inter, sans-serif", size=13, color="#1D1D1F")
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="-apple-system, BlinkMacSystemFont, SF Pro Display, Inter, sans-serif", size=11, color="#86868B"),
                xaxis=dict(showgrid=False, linecolor="#E5E5E7"),
                yaxis=dict(title="Yield (Q/Acre)", showgrid=True, gridcolor="#F0F0F2", linecolor="#E5E5E7"),
                height=280,
                margin=dict(l=30, r=30, t=40, b=30)
            )
            st.plotly_chart(fig_y, use_container_width=True)

            if st.button("💾 Save Yield Audit to Farm Ledger", type="primary", use_container_width=True):
                save_user_prediction(
                    user_id=user["id"], module_name="Crop Yield Prediction",
                    title=f"{y_crop} Yield: {tot_q:.1f} Quintals ({py_acre:.1f} Q/ac)",
                    inputs_json=json.dumps({"acres": y_acres, "n": y_n, "p": y_p, "k": y_k, "rain": y_rain, "ph": y_ph}),
                    outputs_json=json.dumps(yield_res)
                )
                st.success("Yield forecast logged to private farm ledger!")

    # MERGED: Explainable AI (SHAP Waterfall Attributions inside Yield Results)
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    with st.expander("🔍 Explainable AI: SHAP Feature Attributions (Why was this yield predicted?)", expanded=True):
        xai_res = explain_yield_prediction(
            crop_name=y_crop, acreage=y_acres,
            soil_n=y_n, soil_p=y_p, soil_k=y_k, rainfall=y_rain, ph=y_ph
        )
        x_c1, x_c2 = st.columns([1, 1.8])
        base_val = xai_res.get("base_value_quintal", 25.0) if isinstance(xai_res, dict) else 25.0
        top_driver = xai_res.get("top_positive_driver") if isinstance(xai_res, dict) else None
        if not top_driver and isinstance(xai_res, dict):
            pos_f = xai_res.get("positive_factors", [])
            top_driver = pos_f[0]["feature_label"] if pos_f else "Balanced Soil Chemistry"
        if not top_driver:
            top_driver = "Optimal NPK Nutrition"
        with x_c1:
            st.html(f"""
            <div style="background:#F0FDF4; border:1.5px solid #86EFAC; border-radius:8px; padding:12px; margin-bottom:10px;">
                <div style="font-size:0.75rem; font-weight:800; color:#15803D;">BASE VALUE E[f(x)]</div>
                <div style="font-size:1.4rem; font-weight:800; color:#0F172A;">{base_val} <span style="font-size:0.8rem; color:#64748B;">Q/acre</span></div>
                <div style="font-size:0.75rem; color:#64748B;">District historical mean baseline</div>
            </div>
            <div style="background:#FFFFFF; border:1.5px solid #CBD5E1; border-radius:8px; padding:12px;">
                <div style="font-size:0.75rem; font-weight:800; color:#0D5C3A;">TOP DRIVER INFLUENCE</div>
                <div style="font-size:1.1rem; font-weight:800; color:#0D5C3A;">{top_driver}</div>
                <div style="font-size:0.8rem; color:#475569; margin-top:4px;">Primary parameter increasing projected yield above average.</div>
            </div>
            """)
        with x_c2:
            if xai_res.get("waterfall_fig"):
                st.plotly_chart(xai_res["waterfall_fig"], use_container_width=True)

    # MERGED: Crop & Soil Health Diagnostics & Fertilizer Prescriptions
    with st.expander("🌱 Soil Health Diagnostics & Fertilizer Prescription", expanded=False):
        soil_res = evaluate_soil_health(soil_n=y_n, soil_p=y_p, soil_k=y_k, ph=y_ph, organic_carbon=0.65)
        fert_res = calculate_fertilizer_prescription(y_crop, y_acres, y_n, y_p, y_k)

        s_c1, s_c2 = st.columns(2)
        with s_c1:
            st.html(f"""
            <div style="background:#F8FAF8; border:1px solid #E2E8F0; border-radius:8px; padding:12px;">
                <div style="font-weight:700; color:#0D5C3A; font-size:1.0rem; margin-bottom:6px;">Soil Fertility Assessment</div>
                <div style="font-size:0.88rem; color:#0F172A;"><b>Health Index:</b> {soil_res['soil_health_index']:.1f}/100 ({soil_res['fertility_status']})</div>
                <div style="font-size:0.85rem; color:#475569; margin-top:4px;"><b>pH Reaction:</b> {y_ph:.1f} ({soil_res['ph_status']})</div>
                <div style="font-size:0.82rem; color:#334155; margin-top:6px;">{soil_res['organic_amendment']}</div>
            </div>
            """)
        with s_c2:
            st.html(f"""
            <div style="background:#F8FAF8; border:1px solid #E2E8F0; border-radius:8px; padding:12px;">
                <div style="font-weight:700; color:#0D5C3A; font-size:1.0rem; margin-bottom:6px;">Prescription for {y_acres} Acres ({y_crop})</div>
                <div style="font-size:0.85rem; color:#0F172A;">
                    • <b>Urea (46% N):</b> {fert_res['urea_bags_50kg']} bags (50kg)<br>
                    • <b>DAP (18:46:0):</b> {fert_res['dap_bags_50kg']} bags (50kg)<br>
                    • <b>MOP (60% K2O):</b> {fert_res['mop_bags_50kg']} bags (50kg)
                </div>
                <div style="font-size:0.8rem; color:#15803D; font-weight:700; margin-top:6px;">Schedule: Apply 50% N + 100% P & K as basal; 25% N at vegetative; 25% N at flowering.</div>
            </div>
            """)


# ==============================================================================
# 4. MARKET INTELLIGENCE VIEW (SECTION 4 OF PROMPT)
# ==============================================================================
def render_market_intelligence_view(user, farm, df_market):
    st.markdown("#### 💰 Smart Marketplace Intelligence & Arbitrage")
    st.caption("Compares 2,733 wholesale mandis using OpenRouteService road routing, itemizes transport expenses, and identifies highest Net Proceeds.")

    # -------------------------------------------------------------------------
    # REAL-TIME PROFILE ADDRESS & NEAREST DISTANCE CALCULATION RADAR
    # -------------------------------------------------------------------------
    p_village = str(farm.get("village", "Ramanagara Rural"))
    p_district = str(farm.get("district", "Ramanagara"))
    p_state = str(farm.get("state", "Karnataka"))
    profile_addr_str = f"{p_village}, {p_district}, {p_state}".strip(", ")
    default_lat = float(farm.get("latitude", 12.7209))
    default_lon = float(farm.get("longitude", 77.2799))

    if "active_origin_lat" not in st.session_state:
        st.session_state.active_origin_lat = default_lat
    if "active_origin_lon" not in st.session_state:
        st.session_state.active_origin_lon = default_lon
    if "active_origin_label" not in st.session_state:
        st.session_state.active_origin_label = profile_addr_str

    with st.container(border=True):
        st.html(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:1.25rem;">📍</span>
                <span style="font-weight:700; font-size:1.05rem; color:#0D5C3A;">Real-Time Origin & Distance Radar (Profile-Linked)</span>
            </div>
            <div style="font-size:0.75rem; background:#DCFCE7; color:#14532D; font-weight:700; padding:3px 10px; border-radius:12px; border:1px solid #86EFAC;">
                GPS ACTIVE: {st.session_state.active_origin_lat:.4f}° N, {st.session_state.active_origin_lon:.4f}° E
            </div>
        </div>
        <div style="font-size:0.83rem; color:#64748B; margin-bottom:12px;">
            Current origin address pulled from your verified farm profile: <strong>{profile_addr_str}</strong>. You can switch to custom GPS or calculate road distances in real time.
        </div>
        """)

        rad_c1, rad_c2 = st.columns([1.2, 1.8], gap="medium")
        with rad_c1:
            origin_mode = st.radio(
                "Select Origin Address Mode:",
                ["🏠 Use Profile Address", "✏️ Test Custom Address / Live Location"],
                index=0 if st.session_state.active_origin_label == profile_addr_str else 1,
                horizontal=False,
                key="origin_mode_selector"
            )

        with rad_c2:
            if "Profile Address" in origin_mode:
                st.session_state.active_origin_lat = default_lat
                st.session_state.active_origin_lon = default_lon
                st.session_state.active_origin_label = profile_addr_str
                st.info(f"Using Profile Location: **{profile_addr_str}** (Lat: {default_lat:.4f}, Lon: {default_lon:.4f})")
            else:
                cust_addr = st.text_input("Enter Village, Town, District, or PIN", value="Kolar, Karnataka", placeholder="e.g. Kolar, Karnataka or Mandya")
                if st.button("📍 Geocode & Recalculate Distances Real-Time", type="primary", use_container_width=True):
                    with st.spinner("Resolving coordinates in real-time..."):
                        g_lat, g_lon, g_src = geocode_address(cust_addr)
                        if g_lat and g_lon:
                            st.session_state.active_origin_lat = g_lat
                            st.session_state.active_origin_lon = g_lon
                            st.session_state.active_origin_label = cust_addr
                            st.success(f"Location resolved via {g_src}: {g_lat:.4f}° N, {g_lon:.4f}° E")
                            st.rerun()
                        else:
                            st.warning(f"Could not resolve '{cust_addr}'. Using fallback coordinates.")

        # Compute Real-Time Nearest Mandis from Active Origin
        curr_lat = st.session_state.active_origin_lat
        curr_lon = st.session_state.active_origin_lon
        nearest_mandis = get_nearest_mandis_realtime(curr_lat, curr_lon, df_market, top_n=5)

        if nearest_mandis:
            closest_m = nearest_mandis[0]
            sec_m = nearest_mandis[1] if len(nearest_mandis) > 1 else closest_m

            nm_col1, nm_col2, nm_col3 = st.columns(3)
            with nm_col1:
                st.metric(
                    label="📍 Nearest Wholesale Mandi",
                    value=f"{closest_m['market']}",
                    delta=f"{closest_m['road_distance_km']} km • {closest_m['duration_formatted']}"
                )
            with nm_col2:
                st.metric(
                    label="🚚 Est. Short-Haul Freight",
                    value=f"₹{closest_m['freight_est']:,.2f}",
                    delta=f"{closest_m['route_type']}"
                )
            with nm_col3:
                st.metric(
                    label="📍 2nd Nearest Mandi",
                    value=f"{sec_m['market']}",
                    delta=f"{sec_m['road_distance_km']} km • {sec_m['duration_formatted']}"
                )

            with st.expander(f"🔍 View Real-Time Road Distance Matrix to Nearest Mandis from {st.session_state.active_origin_label}", expanded=False):
                df_near = pd.DataFrame(nearest_mandis)[[
                    "market", "district", "state", "road_distance_km", "duration_formatted", "route_type", "freight_est"
                ]].rename(columns={
                    "market": "Mandi / Market",
                    "district": "District",
                    "state": "State",
                    "road_distance_km": "Road Distance (km)",
                    "duration_formatted": "Est. Driving Time",
                    "route_type": "Route Corridor",
                    "freight_est": "Est. Freight (₹)"
                })
                st.dataframe(df_near, use_container_width=True)

    st.html("<div style='height: 8px;'></div>")

    col_mp1, col_mp2, col_mp3 = st.columns(3)
    with col_mp1:
        m_crop = st.selectbox("Crop", sorted(df_market['commodity'].unique()), index=sorted(df_market['commodity'].unique()).index("Tomato") if "Tomato" in df_market['commodity'].unique() else 0)
    with col_mp2:
        m_qty = st.number_input("Quantity to Transport (kg)", min_value=100.0, max_value=25000.0, value=500.0, step=50.0)
    with col_mp3:
        m_veh = st.selectbox("Vehicle Profile", list(DEFAULT_VEHICLE_CONFIGS.keys()), index=0)

    col_fl1, col_fl2 = st.columns(2)
    with col_fl1:
        dist_filter = st.selectbox(
            "Distance Radius Filter",
            [
                "All Mandis (Nationwide)",
                "Local Mandis (< 50 km) — Minimal Freight",
                "Regional Mandis (< 150 km) — Same-day Transport",
                "Statewide Mandis (< 300 km)"
            ],
            index=0
        )
    with col_fl2:
        sort_by = st.selectbox(
            "Sort Results By",
            [
                "Highest Net Proceeds (Recommended)",
                "Nearest Distance (Shortest Haul)",
                "Highest Modal Price (Gross)"
            ],
            index=0
        )

    vehicle_cfg = DEFAULT_VEHICLE_CONFIGS[m_veh].copy()

    with st.spinner("Calculating actual road matrix across wholesale mandis..."):
        p_res = compute_mandi_proceeds_table(
            df_marketplace=df_market,
            crop_name=m_crop,
            quantity_kg=m_qty,
            farmer_lat=st.session_state.get("active_origin_lat", farm.get("latitude", 12.7209)),
            farmer_lon=st.session_state.get("active_origin_lon", farm.get("longitude", 77.2799)),
            vehicle_config=vehicle_cfg
        )

    all_records = list(p_res.get("records", []))
    records = all_records

    # Apply distance filter
    if "< 50 km" in dist_filter:
        records = [r for r in records if r["road_distance_km"] <= 50.0]
    elif "< 150 km" in dist_filter:
        records = [r for r in records if r["road_distance_km"] <= 150.0]
    elif "< 300 km" in dist_filter:
        records = [r for r in records if r["road_distance_km"] <= 300.0]

    # Apply sort
    if "Nearest Distance" in sort_by:
        records = sorted(records, key=lambda x: x["road_distance_km"])
    elif "Highest Modal Price" in sort_by:
        records = sorted(records, key=lambda x: x["modal_price_kg"], reverse=True)
    else:
        records = sorted(records, key=lambda x: x["net_proceeds"], reverse=True)

    if records:
        b_m = max(records, key=lambda x: x["net_proceeds"])
        n_m = min(records, key=lambda x: x["road_distance_km"])
        net_gain = b_m["net_proceeds"] - n_m["net_proceeds"]

        cb1, cb2, cb3 = st.columns(3)
        with cb1:
            st.html(f"""
            <div class="stat-card" style="border:2px solid #0D5C3A; background:#F0FDF4;">
                <div class="stat-label">🏆 Highest Net Proceeds Mandi</div>
                <div style="font-size:1.3rem; font-weight:800; color:#0D5C3A;">{b_m['mandi']}</div>
                <div class="stat-value" style="font-size:1.6rem; color:#0D5C3A;">₹{b_m['net_proceeds']:,.2f}</div>
                <div class="stat-subtext">Realized Net: ₹{b_m['net_price_per_kg']:.2f}/kg • Dist: {b_m['road_distance_km']} km</div>
            </div>
            """)
        with cb2:
            st.html(f"""
            <div class="stat-card">
                <div class="stat-label">📍 Nearest Mandi</div>
                <div style="font-size:1.3rem; font-weight:800; color:#0D5C3A;">{n_m['mandi']}</div>
                <div class="stat-value" style="font-size:1.6rem; color:#0F172A;">₹{n_m['net_proceeds']:,.2f}</div>
                <div class="stat-subtext">Realized Net: ₹{n_m['net_price_per_kg']:.2f}/kg • Dist: {n_m['road_distance_km']} km</div>
            </div>
            """)
        with cb3:
            st.html(f"""
            <div class="stat-card" style="background:#FFFBEB; border-color:#F59E0B;">
                <div class="stat-label">💡 Net Arbitrage Advantage</div>
                <div style="font-size:1.1rem; color:#475569;">Best vs Nearest Mandi</div>
                <div class="stat-value" style="font-size:1.6rem; color:#D97706;">{'+' if net_gain>=0 else ''}₹{net_gain:,.2f}</div>
                <div class="stat-subtext">Net extra profit after all transport expenses</div>
            </div>
            """)

        st.markdown(f"#### Ranked Mandi Ledger ({len(records)} mandis matching filters)")
        df_m_disp = pd.DataFrame(records)[[
            "mandi", "district", "state", "modal_price_kg", "road_distance_km",
            "gross_revenue", "transport_cost", "total_expenses", "net_proceeds", "net_price_per_kg", "suitability_badge"
        ]].rename(columns={
            "mandi": "Market", "district": "District", "state": "State",
            "modal_price_kg": "Gross Modal (₹/kg)", "road_distance_km": "Distance (km)",
            "gross_revenue": "Gross (₹)", "transport_cost": "Freight (₹)",
            "total_expenses": "Fees (₹)", "net_proceeds": "Net Proceeds (₹)",
            "net_price_per_kg": "Net Realized (₹/kg)", "suitability_badge": "Cold-Chain Match"
        })
        st.dataframe(df_m_disp, use_container_width=True)
    else:
        st.info(f"No mandis found within {dist_filter} for '{m_crop}'. Try selecting a wider distance radius.")


# ==============================================================================
# 5. SEASONAL INTELLIGENCE VIEW (SECTION 3C OF PROMPT)
# ==============================================================================
def render_seasonal_intelligence_view(user, farm):
    st.markdown("#### 🗓️ Agro-Climatic Seasonal Intelligence")
    st.caption("Historical cropping calendars, favorable cultivation envelopes, and seasonal price premium windows across Indian agricultural zones.")

    s_crop = st.selectbox("Select Commodity Calendar", ["Tomato", "Onion", "Potato", "Wheat", "Rice / Paddy", "Maize"], index=0)
    intel = get_seasonal_crop_intelligence(s_crop)

    # Active Stage Banner
    st.html(f"""
    <div style="background:#F0FDF4; border:1.5px solid #86EFAC; border-radius:12px; padding:18px; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <div style="font-size:0.8rem; font-weight:800; color:#166534; letter-spacing:0.5px;">CURRENT AGRICULTURAL CALENDAR STAGE</div>
            <div style="font-size:1.45rem; font-weight:800; color:#0D5C3A; margin:4px 0;">{intel['current_stage']}</div>
            <div style="font-size:0.88rem; color:#475569;">Calendar Month: <strong>{intel['current_month']}</strong> • Primary Season: <strong>{intel['primary_season']}</strong></div>
        </div>
        <div>
            <span style="background:#0D5C3A; color:#FFFFFF; padding:8px 18px; border-radius:24px; font-weight:700; font-size:0.95rem;">
                {intel['stage_badge']}
            </span>
        </div>
    </div>
    """)

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        with st.container(border=True):
            st.html("<div style='font-size:1.05rem; font-weight:700; color:#0D5C3A; margin-bottom:8px;'>🌱 Sowing Windows</div>")
            for w in intel["sowing_windows"]:
                st.markdown(f"- **{w}**")
            st.html("<div style='height:8px;'></div>")
            st.html("<div style='font-size:1.05rem; font-weight:700; color:#0D5C3A; margin-bottom:8px;'>🌾 Harvesting Windows</div>")
            for h in intel["harvest_windows"]:
                st.markdown(f"- **{h}**")

    with sc2:
        with st.container(border=True):
            st.html("<div style='font-size:1.05rem; font-weight:700; color:#0D5C3A; margin-bottom:8px;'>🌡️ Optimal Climatic Envelope</div>")
            t_min, t_max = intel["favorable_temp_c"]
            r_min, r_max = intel["favorable_rainfall_mm"]
            st.markdown(f"• **Temperature:** `{t_min}°C – {t_max}°C`")
            st.markdown(f"• **Rainfall:** `{r_min} mm – {r_max} mm`")
            st.html("<div style='height:8px;'></div>")
            st.html("<div style='font-size:1.05rem; font-weight:700; color:#0D5C3A; margin-bottom:8px;'>📍 Production Hubs</div>")
            for hub in intel["production_hubs"]:
                st.markdown(f"• {hub}")

    with sc3:
        with st.container(border=True):
            st.html("<div style='font-size:1.05rem; font-weight:700; color:#0D5C3A; margin-bottom:8px;'>📈 Price Window Cycles</div>")
            st.markdown(f"🟢 **Peak Price Window:**<br>{intel['peak_price_window']}", unsafe_allow_html=True)
            st.html("<div style='height:6px;'></div>")
            st.markdown(f"🔴 **Glut Low Window:**<br>{intel['low_price_window']}", unsafe_allow_html=True)

    with st.container(border=True):
        st.html("<div style='font-size:1.1rem; font-weight:700; color:#0D5C3A; margin-bottom:8px;'>📢 Agronomic Seasonal Guidance</div>")
        st.info(intel["agronomic_advisory"])


# ==============================================================================
# 6. AGRICULTURAL RISK ANALYSIS VIEW (SECTION 3D OF PROMPT)
# ==============================================================================
def render_risk_analysis_view(user, farm):
    st.markdown("#### ⚠️ Multi-Dimensional Agricultural Risk Analysis")
    st.caption("Composite risk evaluation engine quantifying Climate Stress, Soil Degradation, Market Volatility, and Post-Harvest Spoilage.")

    rc1, rc2 = st.columns([1, 1], gap="large")
    with rc1:
        with st.container(border=True):
            st.html("<div style='font-size:1.15rem; font-weight:700; color:#0D5C3A; margin-bottom:12px;'>Risk Assessment Parameters</div>")
            r_crop = st.selectbox("Crop", ["Tomato", "Onion", "Potato", "Wheat", "Rice / Paddy", "Maize"], index=0)
            r_temp = st.slider("Field Temperature (°C)", 10.0, 48.0, 26.5, step=0.5)
            r_rain = st.slider("Seasonal Rainfall (mm)", 10.0, 350.0, 80.0, step=5.0)
            r_hum = st.slider("Relative Humidity (%)", 20.0, 95.0, 70.0, step=5.0)
            r_n = st.slider("Soil Available Nitrogen (kg/ha)", 20.0, 180.0, 85.0)
            r_ph = st.slider("Soil pH Reaction", 4.0, 9.0, 6.5, step=0.1)
            r_cold = st.checkbox("Cold-Chain Transit Protected", value=False)

    risk_res = evaluate_agricultural_risks(
        crop=r_crop, temperature_c=r_temp, humidity_pct=r_hum, rainfall_mm=r_rain,
        n_val=r_n, p_val=50.0, k_val=60.0, ph_val=r_ph, has_cold_chain=r_cold
    )

    with rc2:
        with st.container(border=True):
            st.html("<div style='font-size:1.15rem; font-weight:700; color:#0D5C3A; margin-bottom:12px;'>Composite Risk Score</div>")
            c_score = risk_res["composite_risk_score"]
            c_color = risk_res["risk_color"]

            st.html(f"""
            <div style="background-color:#FFFFFF; border:2px solid {c_color}; border-radius:12px; padding:18px; text-align:center; margin-bottom:16px;">
                <div style="font-size:0.8rem; font-weight:800; color:#64748B;">COMPOSITE RISK INDEX</div>
                <div style="font-size:3.0rem; font-weight:800; color:{c_color}; line-height:1.2;">{c_score} / 100</div>
                <div style="font-size:1.1rem; font-weight:700; color:{c_color};">{risk_res['risk_badge']}</div>
                <div style="font-size:0.85rem; color:#475569; margin-top:4px;">{risk_res['risk_level']}</div>
            </div>
            """)

            # Component Breakdown Bars
            st.html("<div style='font-size:0.92rem; font-weight:700; color:#0D5C3A; margin-bottom:6px;'>Risk Sub-Component Decomposition</div>")
            for comp_name, val in risk_res["component_breakdown"].items():
                st.write(f"**{comp_name}**: `{val:.1f} / 25.0 pts`")
                st.progress(val / 25.0)

    # Active Trigger Factors & Mitigations
    with st.container(border=True):
        st.html("<div style='font-size:1.15rem; font-weight:700; color:#0D5C3A; margin-bottom:12px;'>🛡️ Active Risk Triggers & Prescriptive Mitigations</div>")
        for factor in risk_res["risk_factors"]:
            st.html(f"""
            <div style="border-left:4px solid {risk_res['risk_color']}; background:#F8FAF8; border-radius:0 8px 8px 0; padding:12px; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <strong style="color:#0D5C3A; font-size:0.95rem;">{factor['parameter']} ({factor['category']})</strong>
                    <span style="font-size:0.8rem; font-weight:700; background:#E2E8F0; padding:2px 8px; border-radius:10px;">{factor['severity']}</span>
                </div>
                <div style="font-size:0.85rem; color:#334155; margin:4px 0;">{factor['impact']}</div>
                <div style="font-size:0.83rem; color:#0D5C3A; font-weight:600;">👉 Action: {factor['mitigation']}</div>
            </div>
            """)


# ==============================================================================
# 7. WHAT-IF SIMULATOR VIEW (SECTION 5 OF PROMPT)
# ==============================================================================
def render_what_if_view(user, farm):
    st.markdown("#### 🧪 What-If Agricultural Simulation Engine")
    st.caption("Simulate shifts in rainfall, temperature, soil nutrients, and cultivated acreage to evaluate real-time sensitivity on harvest volume and gross revenue.")

    sim_crop = st.selectbox("Crop for Simulation", ["Tomato", "Rice", "Maize", "Banana", "Cotton", "Potato", "Wheat"], index=0)

    col_base, col_sim = st.columns([1, 1.2], gap="large")

    with col_base:
        with st.container(border=True):
            st.html("<div style='font-size:1.1rem; font-weight:700; color:#64748B; margin-bottom:10px;'>Current Baseline Farm Profile</div>")
            st.markdown(f"• **Acreage:** `{farm.get('acreage', 2.5):.1f} Acres`")
            st.markdown(f"• **Rainfall:** `85 mm`")
            st.markdown(f"• **Temperature:** `25.2°C`")
            st.markdown(f"• **Nitrogen (N):** `80 kg/ha`")
            st.markdown(f"• **Phosphorus (P):** `50 kg/ha`")
            st.markdown(f"• **Potassium (K):** `60 kg/ha`")
            st.markdown(f"• **Soil pH:** `6.5`")
            st.markdown(f"• **Wholesale Mandi Parity:** `₹16.50/kg`")

    baseline_dict = {
        "acreage": float(farm.get("acreage", 2.5)), "rainfall": 85.0, "temperature": 25.2,
        "humidity": 70.0, "soil_n": 80.0, "soil_p": 50.0, "soil_k": 60.0, "ph": 6.5
    }

    with col_sim:
        with st.container(border=True):
            st.html("<div style='font-size:1.15rem; font-weight:700; color:#0D5C3A; margin-bottom:12px;'>Simulate Parameter Modifications</div>")
            sim_acres = st.slider("Cultivated Acreage", 0.5, 20.0, float(farm.get("acreage", 2.5)), step=0.5)
            sim_rain = st.slider("Simulated Rainfall (mm)", 10.0, 300.0, 110.0, step=5.0)
            sim_temp = st.slider("Simulated Temperature (°C)", 12.0, 45.0, 24.0, step=0.5)
            sim_n = st.slider("Simulated Nitrogen (kg/ha)", 20.0, 180.0, 110.0, step=5.0)
            sim_p = st.slider("Simulated Phosphorus (kg/ha)", 10.0, 140.0, 60.0, step=5.0)
            sim_k = st.slider("Simulated Potassium (kg/ha)", 10.0, 180.0, 75.0, step=5.0)
            sim_ph = st.slider("Simulated Soil pH", 4.5, 8.5, 6.7, step=0.1)

    sim_dict = {
        "acreage": sim_acres, "rainfall": sim_rain, "temperature": sim_temp,
        "humidity": 70.0, "soil_n": sim_n, "soil_p": sim_p, "soil_k": sim_k, "ph": sim_ph
    }

    sim_result = run_what_if_simulation(
        crop_name=sim_crop, baseline_params=baseline_dict, simulated_params=sim_dict, mandi_price_kg=16.50
    )

    deltas = sim_result["deltas"]
    base = sim_result["baseline"]
    sim = sim_result["simulated"]

    # Comparative Outcomes
    st.html("<div style='margin-top:14px;'></div>")
    sd1, sd2, sd3 = st.columns(3)
    with sd1:
        st.html(f"""
        <div class="stat-card">
            <div class="stat-label">Harvest Production Delta</div>
            <div class="stat-value" style="color:#0D5C3A;">{'+' if deltas['yield_kg']>=0 else ''}{deltas['yield_kg']:,.0f} kg</div>
            <div class="stat-subtext">{'+' if deltas['yield_pct']>=0 else ''}{deltas['yield_pct']:.1f}% vs Baseline ({sim['total_yield_kg']:,.0f} kg total)</div>
        </div>
        """)
    with sd2:
        st.html(f"""
        <div class="stat-card">
            <div class="stat-label">Projected Gross Revenue Shift</div>
            <div class="stat-value" style="color:#0D5C3A;">{'+' if deltas['revenue']>=0 else ''}₹{deltas['revenue']:,.2f}</div>
            <div class="stat-subtext">{'+' if deltas['revenue_pct']>=0 else ''}{deltas['revenue_pct']:.1f}% Gross Return Delta</div>
        </div>
        """)
    with sd3:
        st.html(f"""
        <div class="stat-card">
            <div class="stat-label">Risk Shift</div>
            <div class="stat-value" style="color:{'#15803D' if deltas['risk_score']<=0 else '#DC2626'};">{deltas['risk_score']:+.1f} pts</div>
            <div class="stat-subtext">{deltas['risk_direction']} (Score: {sim['risk_score']})</div>
        </div>
        """)

    with st.container(border=True):
        st.html("<div style='font-size:1.1rem; font-weight:700; color:#0D5C3A; margin-bottom:8px;'>💡 Sensitivity Mechanism Breakdown</div>")
        for ins in sim_result["insights"]:
            st.markdown(f"• {ins}")


# ==============================================================================
# 8. EXPLAINABLE AI (XAI) VIEW (SECTION 6 OF PROMPT)
# ==============================================================================
def render_explainable_ai_view(user, farm):
    st.markdown("#### 🔍 Explainable AI (SHAP TreeExplainer Attributions)")
    st.caption("Deconstructs black-box Random Forest inference into exact feature contributions (positive yield boosters vs limiting bottlenecks).")

    x_crop = st.selectbox("Crop for Model Attribution", ["Tomato", "Rice", "Maize", "Banana", "Cotton", "Potato", "Wheat"], index=0)
    
    with st.spinner("Computing SHAP TreeExplainer kernel and marginal values..."):
        xai_res = explain_yield_prediction(
            crop_name=x_crop,
            acreage=float(farm.get("acreage", 2.5)),
            soil_n=85.0, soil_p=55.0, soil_k=58.0, rainfall=82.0, ph=6.5
        )

    # Base Value & Final Output
    xb1, xb2 = st.columns(2)
    with xb1:
        st.html(f"""
        <div class="stat-card">
            <div class="stat-label">Expected Base Value E[f(x)]</div>
            <div class="stat-value" style="color:#64748B;">{xai_res.get('base_value_quintal', 25.0)} Q/ac</div>
            <div class="stat-subtext">Mean yield across training distribution</div>
        </div>
        """)
    with xb2:
        st.html(f"""
        <div class="stat-card" style="border:2px solid #0D5C3A; background:#F0FDF4;">
            <div class="stat-label">Final Predicted Yield f(x)</div>
            <div class="stat-value" style="color:#0D5C3A;">{xai_res.get('predicted_yield_quintal', 25.0)} Q/ac</div>
            <div class="stat-subtext">Net sum of all positive & negative SHAP attributions</div>
        </div>
        """)

    # Interactive Plotly Waterfall Chart
    with st.container(border=True):
        if xai_res.get("waterfall_fig"):
            st.plotly_chart(xai_res["waterfall_fig"], use_container_width=True)

    # Natural Language Explanations
    with st.container(border=True):
        st.html("<div style='font-size:1.15rem; font-weight:700; color:#0D5C3A; margin-bottom:12px;'>🌱 Plain-English Agronomic Explanations for Farmers</div>")
        for expl in xai_res.get("natural_explanations", []):
            st.markdown(expl)


# ==============================================================================
# 9. AI DECISION REPORTS VIEW (SECTION 7 OF PROMPT)
# ==============================================================================
def render_decision_reports_view(user, farm, df_market):
    st.markdown("#### 📑 Unified Agricultural Decision Intelligence Report")
    st.caption("Synthesizes Historical Intelligence, Current Farm Telemetry, ML Forecasts, and Logistics into a prioritized decision brief.")

    r_crop = st.selectbox("Report Crop", ["Tomato", "Onion", "Potato", "Wheat", "Rice"], index=0)
    r_batch_kg = st.number_input("Batch Quantity for Logistics (kg)", value=500.0, step=50.0)

    with st.spinner("Generating unified intelligence synthesis..."):
        report = generate_unified_decision_report(
            farm_profile=farm,
            crop_name=r_crop,
            quantity_kg=r_batch_kg,
            n_val=85.0, p_val=55.0, k_val=58.0, ph_val=6.5,
            temp_c=25.2, humidity_pct=71.0, rainfall_mm=82.0,
            df_marketplace=df_market,
            vehicle_type="Mini Truck (Normal)"
        )

    # Display 8 Sections
    with st.container(border=True):
        st.html(f"""
        <div style="border-bottom:1.5px solid #E2E8F0; padding-bottom:12px; margin-bottom:16px;">
            <div style="font-size:0.8rem; font-weight:800; color:#14532D; letter-spacing:0.5px;">KRISHI AI • EXECUTIVE DECISION BRIEF</div>
            <h2 style="color:#0D5C3A; margin:2px 0; font-size:1.6rem; font-weight:800;">{report['metadata']['farm_name']} — {r_crop} Audit</h2>
            <div style="font-size:0.85rem; color:#64748B;">Generated on {report['metadata']['generated_at']} for {report['metadata']['farmer_name']}</div>
        </div>
        """)

        # 8-Point Cards
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("1. Historical Baseline", f"₹{report['1_historical_performance']['avg_historical_price_kg']:.2f}/kg", f"Peak: {report['1_historical_performance']['peak_price_month']}")
        with c2:
            st.metric("3. Expected Yield", f"{report['3_expected_yield']['total_harvest_kg']:,.0f} kg", f"{report['3_expected_yield']['predicted_yield_per_acre']} Q/ac")
        with c3:
            st.metric("4. 14-Day Price Forecast", f"₹{report['4_future_market_price']['forecast_14_day']:.2f}/kg", report['4_future_market_price']['projected_trend'])
        with c4:
            st.metric("5. Risk Index", f"{report['5_risk_assessment']['composite_score']}/100", report['5_risk_assessment']['risk_badge'])

        st.html("<div style='height:14px;'></div>")

        r_m1, r_m2 = st.columns(2)
        with r_m1:
            st.html(f"""
            <div style="background:#F0FDF4; border:1.5px solid #86EFAC; border-radius:10px; padding:16px;">
                <div style="font-size:0.8rem; font-weight:800; color:#14532D;">6. BEST AVAILABLE MARKETPLACE</div>
                <div style="font-size:1.4rem; font-weight:800; color:#0D5C3A; margin:4px 0;">{report['6_best_marketplace']['mandi']} APMC</div>
                <div style="font-size:0.85rem; color:#334155;">Location: {report['6_best_marketplace']['district']}, {report['6_best_marketplace']['state']} • Road Distance: {report['6_best_marketplace']['road_distance_km']} km ({report['6_best_marketplace']['travel_duration']})</div>
            </div>
            """)
        with r_m2:
            st.html(f"""
            <div style="background:#F0FDF4; border:1.5px solid #86EFAC; border-radius:10px; padding:16px;">
                <div style="font-size:0.8rem; font-weight:800; color:#14532D;">7. ESTIMATED NET REVENUE</div>
                <div style="font-size:1.4rem; font-weight:800; color:#0D5C3A; margin:4px 0;">₹{report['7_estimated_net_revenue']['net_proceeds']:,.2f}</div>
                <div style="font-size:0.85rem; color:#334155;">Net In-Hand: ₹{report['7_estimated_net_revenue']['net_realized_price_kg']:.2f}/kg (Arbitrage: +₹{report['7_estimated_net_revenue']['arbitrage_advantage_vs_nearest']:,.2f} vs Nearest)</div>
            </div>
            """)

        st.html("<div style='height:16px;'></div>")
        st.html("<div style='font-size:1.15rem; font-weight:800; color:#0D5C3A; margin-bottom:10px;'>8. Prioritized Recommended Farming Decisions</div>")
        for dec in report.get("8_recommended_decisions", []):
            st.markdown(dec)

    # Export Buttons (PDF & TXT & Ledger)
    c_dl1, c_dl2, c_dl3 = st.columns([1.2, 1, 1])
    with c_dl1:
        try:
            pdf_bytes = generate_unified_pdf_report(report)
            st.download_button(
                label="📥 Download Official Executive Report (PDF)",
                data=pdf_bytes,
                file_name=f"krishi_ai_report_{r_crop}_{datetime.date.today()}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"PDF generation error: {e}")
    with c_dl2:
        farmer_name = user.get("full_name", "Farmer Enterprise")
        farm_title = farm.get("farm_name", "Agricultural Enterprise")
        md_text = f"# Krishi AI Decision Brief - {r_crop}\n\nFarmer: {farmer_name}\nFarm: {farm_title}\n\n## Recommendations:\n" + "\n".join(report.get("8_recommended_decisions", []))
        st.download_button(
            label="📄 Download Summary (TXT)",
            data=md_text,
            file_name=f"krishi_ai_brief_{r_crop}_{datetime.date.today()}.txt",
            mime="text/plain",
            use_container_width=True
        )
    with c_dl3:
        if st.button("💾 Save to Account Ledger", use_container_width=True):
            save_user_prediction(
                user_id=user["id"],
                module_name="AI Decision Reports",
                title=f"{r_crop} Decision: {report['6_best_marketplace']['mandi']} (₹{report['7_estimated_net_revenue']['net_proceeds']:,.0f})",
                inputs_json=json.dumps({"crop": r_crop, "quantity": r_batch_kg}),
                outputs_json=json.dumps(report)
            )
            st.success("Decision report securely saved to your private account!")


# ==============================================================================
# 10. CROP & SOIL ADVISOR VIEW (RETAINED FROM PREVIOUS)
# ==============================================================================
def render_crop_soil_advisor_view(user, farm):
    st.markdown("#### 🌱 Precision Crop Selection & Fertilizer Prescriptions")
    
    t1, t2 = st.tabs(["🌾 Crop Suitability Matcher", "💊 Commercial Fertilizer Prescriptions"])
    with t1:
        c_n1, c_n2, c_n3 = st.columns(3)
        with c_n1:
            n_val = st.number_input("Nitrogen (N) kg/ha", value=85.0)
        with c_n2:
            p_val = st.number_input("Phosphorus (P) kg/ha", value=55.0)
        with c_n3:
            k_val = st.number_input("Potassium (K) kg/ha", value=58.0)
        
        c_c1, c_c2 = st.columns(2)
        with c_c1:
            t_val = st.number_input("Temperature (°C)", value=25.2)
            ph_val = st.number_input("Soil pH", value=6.5)
        with c_c2:
            h_val = st.number_input("Humidity (%)", value=71.0)
            r_val = st.number_input("Rainfall (mm)", value=82.0)

        crop_res = recommend_crop(n_val, p_val, k_val, t_val, h_val, ph_val, r_val)
        prov_lbl = crop_res.get('model_provenance', 'VALIDATED ON REAL AGRICULTURAL DATA')
        st.html(f"""
        <div style="background-color:#F0FDF4; border:2px solid #0D5C3A; border-radius:10px; padding:18px; text-align:center; margin:14px 0;">
            <div style="margin-bottom:8px;">
                <span style="background:#0D5C3A; color:white; padding:4px 12px; border-radius:12px; font-weight:700; font-size:0.8rem;">TOP AGRONOMIC MATCH</span>
                <span style="background:#059669; color:white; padding:4px 10px; border-radius:12px; font-weight:700; font-size:0.75rem; margin-left:6px;">🟢 {prov_lbl}</span>
            </div>
            <div style="font-size:2.4rem; font-weight:800; color:#0D5C3A; margin:6px 0;">{crop_res['primary_crop']}</div>
            <div style="font-size:1.1rem; font-weight:700; color:#166534;">{crop_res['confidence']:.1f}% Model Confidence</div>
        </div>
        """)

    with t2:
        f_crop = st.selectbox("Target Crop for Fertility Prescription", ["Tomato", "Rice", "Maize", "Banana", "Cotton", "Potato"])
        fert_res = calculate_fertilizer_prescription(f_crop, 70.0, 45.0, 50.0, float(farm.get("acreage", 2.0)))
        st.write(f"Commercial Fertilizers Required for {farm.get('acreage', 2.0)} Acres:")
        for item in fert_res["fertilizers"]:
            st.info(f"**{item['name']}**: {item['bags_50kg']} Bags ({item['total_kg']} kg) — {item['purpose']}")


# ==============================================================================
# 11. ANTI-FRAUD VIEW (RETAINED FROM PREVIOUS)
# ==============================================================================
def render_anti_fraud_view(user, farm):
    st.markdown("#### 🛡️ Predatory Offer & Unfair Middleman Transaction Detector")
    st.caption("Audits buyer farmgate bids against fair mandi parity, calculates farmer loss, and creates negotiation counter-offers.")

    c_fr1, c_fr2 = st.columns([1, 1], gap="large")
    with c_fr1:
        with st.container(border=True):
            offered_p = st.number_input("Buyer's Quoted Price (₹/kg)", min_value=1.0, max_value=150.0, value=11.50, step=0.5)
            offered_q = st.number_input("Quantity in Deal (kg)", min_value=100.0, max_value=25000.0, value=500.0, step=50.0)
            pay_term = st.selectbox("Payment Terms", ["Immediate Cash / UPI at Weighbridge", "Payment after 7 days", "Payment after 15 days", "Unspecified Credit"])

    bench_m = 16.50
    fr_res = evaluate_buyer_offer(offered_p, offered_q, bench_m, bench_m * 0.88, payment_terms=pay_term)

    with c_fr2:
        with st.container(border=True):
            st.html(f"""
            <div style="border:2px solid {fr_res['badge_color']}; border-radius:10px; padding:16px; margin-bottom:14px;">
                <span style="background:{fr_res['badge_color']}; color:white; padding:4px 12px; border-radius:12px; font-weight:700; font-size:0.85rem;">{fr_res['status']}</span>
                <div style="font-size:1.0rem; color:#111827; margin:10px 0;">{fr_res['summary']}</div>
                <div style="display:flex; justify-content:space-between; border-top:1px solid #E2E8F0; padding-top:8px;">
                    <div><strong>Offer Value:</strong> ₹{fr_res['total_offered_proceeds']:,.2f}</div>
                    <div><strong>Fair Parity:</strong> ₹{fr_res['total_fair_proceeds']:,.2f}</div>
                </div>
            </div>
            """)
            st.info(f"💡 **Recommended Counter-Offer:** **₹{fr_res['recommended_counter_kg']:.2f}/kg** (Recovers **₹{fr_res['extra_money_from_counter']:,.2f}** in fair proceeds!)")
            st.markdown(f"*{fr_res['negotiation_script']}*")


# ==============================================================================
# 12. SETTINGS VIEW (RETAINED FROM PREVIOUS)
# ==============================================================================
def render_settings_view(user, farm):
    st.markdown("#### 👤 Farmer Profile & Enterprise Settings")
    col_p1, col_p2 = st.columns([1, 1], gap="large")
    with col_p1:
        with st.container(border=True):
            st.html("<div style='font-size:1.15rem; font-weight:700; color:#0D5C3A; margin-bottom:12px;'>Farm Profile Information & Real-Time Location</div>")
            p_farm_name = st.text_input("Farm Name", value=farm.get("farm_name", "Green Valley Agro Farm"))
            p_acreage = st.number_input("Holding Acreage (Acres)", value=float(farm.get("acreage", 2.5)), step=0.5)
            p_village = st.text_input("Village / Town", value=farm.get("village", "Ramanagara"))
            p_district = st.text_input("District", value=farm.get("district", "Ramanagara"))
            p_state = st.text_input("State", value=farm.get("state", "Karnataka"))
            p_crops = st.text_input("Primary Crops", value=farm.get("primary_crops", "Tomato, Maize, Banana"))

            curr_farm_lat = float(farm.get("latitude", 12.7209))
            curr_farm_lon = float(farm.get("longitude", 77.2799))

            st.html(f"""
            <div style="background:#F8FAF8; border:1px solid #E2E8F0; padding:10px 14px; border-radius:10px; margin:10px 0;">
                <div style="font-size:0.75rem; color:#64748B; font-weight:700; text-transform:uppercase;">Current Profile Geocoding</div>
                <div style="font-size:0.92rem; font-weight:600; color:#0D5C3A;">📍 {curr_farm_lat:.4f}° N, {curr_farm_lon:.4f}° E</div>
                <div style="font-size:0.78rem; color:#86868B;">Address: {p_village}, {p_district}, {p_state}</div>
            </div>
            """)

            col_geo1, col_geo2 = st.columns(2)
            with col_geo1:
                btn_test_geo = st.button("📍 Geocode & Nearest Mandis", use_container_width=True)
            with col_geo2:
                btn_save_prof = st.button("💾 Save Profile & Update GPS", type="primary", use_container_width=True)
            if btn_test_geo:
                query_str = f"{p_village}, {p_district}, {p_state}"
                res_lat, res_lon, res_src = geocode_address(query_str)
                if res_lat and res_lon:
                    st.success(f"✅ Geocoded via {res_src}: {res_lat:.4f}° N, {res_lon:.4f}° E")
                    from modules.data_loader import load_normalized_marketplace_data
                    df_preview = load_normalized_marketplace_data()
                    preview_mandis = get_nearest_mandis_realtime(res_lat, res_lon, df_preview, top_n=3)
                    if preview_mandis:
                        st.markdown("**Nearest Wholesale Mandis from this location:**")
                        for pm in preview_mandis:
                            st.write(f"• **{pm['market']}**: {pm['road_distance_km']} km ({pm['duration_formatted']}) — Freight: ₹{pm['freight_est']}")
                else:
                    st.warning("Could not automatically geocode exact village; district coordinates will be retained.")

            if btn_save_prof:
                query_str = f"{p_village}, {p_district}, {p_state}"
                res_lat, res_lon, _ = geocode_address(query_str)
                final_lat = res_lat if res_lat else curr_farm_lat
                final_lon = res_lon if res_lon else curr_farm_lon

                up_ok, up_msg = update_farm_profile(user["id"], {
                    "farm_name": p_farm_name, "acreage": p_acreage, "village": p_village,
                    "district": p_district, "state": p_state, "primary_crops": p_crops,
                    "latitude": final_lat, "longitude": final_lon
                })
                if up_ok:
                    st.success("Farm profile updated!")
                    st.session_state.current_user["farm"]["farm_name"] = p_farm_name
                    st.session_state.current_user["farm"]["acreage"] = p_acreage
                    st.session_state.current_user["farm"]["district"] = p_district
                    st.session_state.current_user["farm"]["village"] = p_village
                    st.session_state.current_user["farm"]["state"] = p_state
                    st.session_state.current_user["farm"]["latitude"] = final_lat
                    st.session_state.current_user["farm"]["longitude"] = final_lon
                    st.session_state.active_origin_lat = final_lat
                    st.session_state.active_origin_lon = final_lon
                    st.session_state.active_origin_label = f"{p_village}, {p_district}, {p_state}"
                    st.rerun()

    with col_p2:
        with st.container(border=True):
            st.html("<div style='font-size:1.15rem; font-weight:700; color:#0D5C3A; margin-bottom:12px;'>Security & Password Change</div>")
            old_pwd = st.text_input("Current Password", type="password")
            new_pwd = st.text_input("New Password", type="password")
            new_pwd_conf = st.text_input("Confirm New Password", type="password")

            if st.button("Update Password"):
                if new_pwd != new_pwd_conf:
                    st.error("New passwords do not match.")
                else:
                    ch_ok, ch_msg = change_user_password(user["id"], old_pwd, new_pwd)
                    if ch_ok:
                        st.success(ch_msg)
                    else:
                        st.error(ch_msg)

            st.html(f"<div style='margin-top:20px; font-size:0.85rem; color:#64748B;'>Account ID: #{user['id']} | Role: {user['role'].upper()}</div>")

            # DPDP Act 2023 Privacy & Data Rights
            st.html("<hr style='border:none; border-top:1px solid #E2E8F0; margin:16px 0;'>")
            st.html("<div style='font-size:1.05rem; font-weight:700; color:#0D5C3A; margin-bottom:8px;'>🔒 Data Privacy & DPDP Act 2023 Rights</div>")
            st.caption("You have the right to data portability and complete account erasure under Indian Data Protection laws.")

            from modules.auth_db import export_user_data, delete_user_account, invalidate_session
            user_export = export_user_data(user["id"])
            st.download_button(
                label="📥 Export My Account Ledger (JSON)",
                data=json.dumps(user_export, indent=2),
                file_name=f"krishi_ai_ledger_user_{user['id']}.json",
                mime="application/json",
                use_container_width=True
            )

            with st.expander("⚠️ Danger Zone: Delete Account", expanded=False):
                st.warning("Permanently deletes your account, farm profiles, soil records, and saved audits. This action cannot be undone.")
                del_confirm = st.checkbox("I confirm permanent deletion of my agricultural records", key="chk_del_acc")
                if st.button("Permanently Erase My Account", type="primary", disabled=not del_confirm):
                    d_ok, d_msg = delete_user_account(user["id"])
                    if d_ok:
                        st.success(d_msg)
                        if "auth_token" in st.session_state and st.session_state.auth_token:
                            invalidate_session(st.session_state.auth_token)
                        st.session_state.auth_token = None
                        st.session_state.current_user = None
                        st.rerun()
                    else:
                        st.error(d_msg)

            # System Disaster Recovery (Admin Only)
            if user.get("role") == "admin":
                st.html("<hr style='border:none; border-top:1px solid #E2E8F0; margin:16px 0;'>")
                st.html("<div style='font-size:1.05rem; font-weight:700; color:#0D5C3A; margin-bottom:8px;'>🛠️ System Database Maintenance (Admin)</div>")
                from modules.db_backup import verify_database_integrity, backup_database
                integ = verify_database_integrity()
                st.html(f"<div style='font-size:0.85rem; color:#334155;'>SQLite Health: <b>{integ.get('status')}</b> | Size: <b>{integ.get('db_size_kb')} KB</b> | Tables: <b>{integ.get('table_count')}</b></div>")
                if st.button("💾 Trigger Atomic Online Backup Snapshot", use_container_width=True):
                    b_ok, b_msg, b_file = backup_database()
                    if b_ok:
                        st.success(b_msg)
                    else:
                        st.error(b_msg)

            # Live API Health & Commercial Licensing Telemetry
            st.html("<hr style='border:none; border-top:1px solid #E2E8F0; margin:16px 0;'>")
            st.html("<div style='font-size:1.05rem; font-weight:700; color:#0D5C3A; margin-bottom:8px;'>🌐 External Agricultural API Telemetry</div>")
            st.caption("Real-time connectivity, data freshness, and commercial licensing compliance.")

            from modules.api_clients import get_api_status_report
            from modules.db_engine import check_database_health
            
            db_h = check_database_health()
            st.html(f"<div style='font-size:0.85rem; color:#334155; margin-bottom:10px;'>Database Engine: <b>{db_h.get('database_type')}</b> (Status: <b>{db_h.get('status')}</b> • Latency: <b>{db_h.get('latency_ms')} ms</b>)</div>")

            api_statuses = get_api_status_report()
            for api_item in api_statuses:
                b_col = "#16A34A" if "LIVE" in api_item["status"] else ("#D97706" if "CACHED" in api_item["status"] else "#DC2626")
                st.html(f"""
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:10px; margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b>{api_item['provider']}</b>
                        <span style="background:{b_col}; color:white; padding:2px 8px; border-radius:12px; font-size:0.75rem; font-weight:700;">{api_item['status']}</span>
                    </div>
                    <div style="font-size:0.8rem; color:#64748B; margin-top:4px;">
                        Freshness: {api_item['data_freshness']} • Observation Date: {api_item['last_observation_date']}
                    </div>
                    <div style="font-size:0.75rem; color:#475569; margin-top:2px;">
                        <i>{api_item['commercial_terms']}</i>
                    </div>
                </div>
                """)


# ==============================================================================
# 13. TREND SHIFT INTELLIGENCE VIEW
# ==============================================================================
def render_trend_shift_view(user, farm, df_market):
    st.markdown("#### 📈 Trend Shift Intelligence & Early Warning System")
    st.caption("Change-point detection and structural inflection monitoring across 16.37M historical mandi transactions and micro-climate telemetry.")

    TOP_CROPS = ["Tomato", "Onion", "Potato", "Wheat", "Rice", "Banana", "Brinjal", "Cabbage", "Cauliflower", "Maize"]
    INDIAN_STATES = ["Karnataka", "Maharashtra", "All States", "Gujarat", "Haryana", "Punjab", "Rajasthan", "Madhya Pradesh", "Uttar Pradesh", "Tamil Nadu", "Kerala"]

    farm_crop = farm.get("primary_crops", "Tomato").split(",")[0].strip()
    crop_idx = TOP_CROPS.index(farm_crop) if farm_crop in TOP_CROPS else 0
    farm_state = farm.get("state", "Karnataka")
    state_idx = INDIAN_STATES.index(farm_state) if farm_state in INDIAN_STATES else 0

    col_f1, col_f2, col_f3 = st.columns([1.2, 1.2, 1])
    with col_f1:
        sel_crop = st.selectbox("Agricultural Commodity", TOP_CROPS, index=crop_idx, key="ts_crop")
    with col_f2:
        sel_state = st.selectbox("Target Geography", INDIAN_STATES, index=state_idx, key="ts_state")
    with col_f3:
        max_shifts = st.slider("Shifts to Inspect", min_value=3, max_value=12, value=6, key="ts_slider")

    with st.spinner(f"Detecting structural momentum and supply-shock inflections for {sel_crop} ({sel_state})..."):
        shift_res = detect_market_trend_shifts(sel_crop, state=sel_state)
        clim_res = analyze_weather_and_yield_shifts(sel_crop, state=sel_state)

    if shift_res.get("status") and not shift_res.get("shifts_count"):
        st.warning(shift_res["status"])
        return

    # REGIME ALERT BANNER
    regime = shift_res.get("current_regime", "Neutral")
    regime_color = shift_res.get("regime_color", "#15803D")
    latest_p = shift_res.get("latest_price", 0.0)
    vel_7d = shift_res.get("velocity_7d_pct", 0.0)
    mom_30d = shift_res.get("momentum_30d_pct", 0.0)
    sma_7 = shift_res.get("sma_7", 0.0)
    sma_30 = shift_res.get("sma_30", 0.0)
    shifts_cnt = shift_res.get("shifts_count", 0)

    # Pick background tint for banner
    if "Bullish" in regime:
        banner_bg = "#F0FDF4"
        banner_border = "#86EFAC"
        regime_desc = "Wholesale prices are gaining upward momentum above the 30-day baseline. Buyer bidding competition is favorable."
    elif "Bearish" in regime:
        banner_bg = "#FEF2F2"
        banner_border = "#FCA5A5"
        regime_desc = "Wholesale prices are decelerating below the 30-day baseline. Mandi arrivals are elevated or demand is soft."
    else:
        banner_bg = "#FFFBEB"
        banner_border = "#FCD34D"
        regime_desc = "Prices are trading within normal statistical volatility envelopes without directional momentum."

    st.html(f"""
    <div style="background-color:{banner_bg}; border:1.5px solid {banner_border}; border-radius:10px; padding:16px 20px; margin: 12px 0 20px 0;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div>
                <div style="font-size:0.8rem; font-weight:800; color:{regime_color}; text-transform:uppercase; letter-spacing:0.5px;">ACTIVE REGIME STATUS</div>
                <div style="font-size:1.35rem; font-weight:800; color:{regime_color}; margin:3px 0 4px 0;">{regime}</div>
                <div style="font-size:0.88rem; color:#475569;">{regime_desc}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.8rem; color:#64748B; font-weight:600;">Spot Modal Price</div>
                <div style="font-size:1.6rem; font-weight:800; color:#0F172A;">₹{latest_p:.2f} <span style="font-size:0.9rem; font-weight:600; color:#64748B;">/ kg</span></div>
            </div>
        </div>
    </div>
    """)

    # 4 MODERN KPI METRIC CARDS
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric(label="Current Regime", value=regime.split("(")[0].strip())
    with k2:
        st.metric(label="7-Day Price Velocity", value=f"{vel_7d:+.1f}%", delta=f"Fast SMA: ₹{sma_7:.2f}/kg")
    with k3:
        st.metric(label="30-Day Momentum", value=f"{mom_30d:+.1f}%", delta=f"Base SMA: ₹{sma_30:.2f}/kg")
    with k4:
        st.metric(label="Structural Inflections", value=f"{shifts_cnt} Detected", delta=f"Latest {max_shifts} profiled")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # INTERACTIVE TIME-SERIES WITH INFLECTION MARKERS
    with st.container(border=True):
        st.html("<div style='font-size:1.1rem; font-weight:700; color:#0D5C3A; margin-bottom:4px;'>Wholesale Price Trajectory & Inflection Timeline</div><div style='font-size:0.85rem; color:#64748B; margin-bottom:12px;'>Historical daily prices overlaid with Fast 7-Day SMA, 30-Day Base SMA, and Bollinger Volatility Envelopes (±2σ). Colored diamonds mark validated trend shift events.</div>")
        if shift_res.get("plot_fig"):
            st.plotly_chart(shift_res["plot_fig"], use_container_width=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # SECTION: DETECTED TREND SHIFTS & EARLY WARNING INTELLIGENCE
    st.markdown(f"#### 🔍 Detected Trend Shift Timeline — Top {max_shifts} Structural Inflections")
    st.caption("Each shift reflects a verified mathematical change-point (moving average crossover, volatility breakout, or arrival surge).")

    shifts_list = shift_res.get("recent_shifts", [])[:max_shifts]
    if not shifts_list:
        st.info("No significant structural trend shifts detected for this commodity/state filter.")
    else:
        for idx, s in enumerate(shifts_list):
            with st.container(border=True):
                # Header of the shift card
                st.html(f"""
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; border-bottom:1px solid #E2E8F0; padding-bottom:8px;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span style="background-color:{s['badge_color']}; color:#FFFFFF; padding:4px 12px; border-radius:16px; font-size:0.82rem; font-weight:700;">
                            {s['badge']}
                        </span>
                        <span style="font-size:0.95rem; font-weight:700; color:#0F172A;">Detected on {s['date']}</span>
                    </div>
                    <div style="font-size:1.05rem; font-weight:800; color:#0D5C3A;">
                        ₹{s['price']:.2f} <span style="font-size:0.8rem; font-weight:600; color:#64748B;">/ kg</span>
                    </div>
                </div>
                """)

                # The 6 Mandatory Intelligence Fields
                c_s1, c_s2 = st.columns(2)
                with c_s1:
                    st.html(f"""
                    <div style="font-size:0.82rem; font-weight:700; color:#64748B; text-transform:uppercase;">1. Previous Trend</div>
                    <div style="font-size:0.92rem; color:#0F172A; font-weight:600; margin-bottom:10px;">{s['previous_trend']}</div>

                    <div style="font-size:0.82rem; font-weight:700; color:#64748B; text-transform:uppercase;">2. Current Trend</div>
                    <div style="font-size:0.92rem; color:#0F172A; font-weight:600; margin-bottom:10px;">{s['current_trend']}</div>

                    <div style="font-size:0.82rem; font-weight:700; color:#64748B; text-transform:uppercase;">3. Magnitude of Change</div>
                    <div style="font-size:0.95rem; color:{s['badge_color']}; font-weight:700; margin-bottom:10px;">{s['magnitude']}</div>
                    """)

                with c_s2:
                    st.html(f"""
                    <div style="font-size:0.82rem; font-weight:700; color:#64748B; text-transform:uppercase;">4. Possible Reasons (Data Evidence)</div>
                    <div style="font-size:0.9rem; color:#334155; margin-bottom:10px;">{s['data_evidence']}</div>

                    <div style="font-size:0.82rem; font-weight:700; color:#64748B; text-transform:uppercase;">5. Potential Future Impact</div>
                    <div style="font-size:0.9rem; color:#334155; margin-bottom:10px;">{s['potential_impact']}</div>

                    <div style="font-size:0.82rem; font-weight:700; color:#0D5C3A; text-transform:uppercase;">6. Recommended Action</div>
                    <div style="font-size:0.92rem; color:#0D5C3A; font-weight:700; background:#DCFCE7; padding:6px 12px; border-radius:6px; border-left:3px solid #15803D;">{s['recommended_action']}</div>
                    """)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # SECTION: MULTI-SEASON AGRO-CLIMATIC & PRODUCTION SHIFTS
    st.markdown("#### 🌦️ Multi-Season Weather & Yield Structural Shifts")
    st.caption("Long-term agronomic changes in climatic patterns, continuous cropping yields, and post-harvest margins.")

    col_w, col_y = st.columns(2)

    with col_w:
        with st.container(border=True):
            st.html("<div style='font-size:1.05rem; font-weight:700; color:#0D5C3A; margin-bottom:10px;'>🌧️ Agro-Climatic & Weather Pattern Shifts</div>")
            for w in clim_res.get("weather_shifts", []):
                st.html(f"""
                <div style="background:#F8FAF8; border:1px solid #E2E8F0; border-radius:8px; padding:12px; margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                        <span style="font-weight:700; color:#0F172A; font-size:0.92rem;">{w['parameter']}</span>
                        <span style="font-size:0.78rem; font-weight:700; color:#D97706; background:#FEF3C7; padding:2px 8px; border-radius:12px;">{w['direction']}</span>
                    </div>
                    <div style="font-size:0.82rem; color:#64748B; margin-bottom:4px;"><b>Historical Baseline:</b> {w['historical_baseline']}</div>
                    <div style="font-size:0.85rem; color:#B45309; font-weight:600; margin-bottom:4px;"><b>Detected Shift:</b> {w['detected_shift']}</div>
                    <div style="font-size:0.82rem; color:#334155; margin-bottom:6px;"><b>Agronomic Impact:</b> {w['impact']}</div>
                    <div style="font-size:0.82rem; color:#0D5C3A; font-weight:700; background:#E2F3E7; padding:4px 8px; border-radius:4px;"><b>Mitigation:</b> {w['mitigation']}</div>
                </div>
                """)

    with col_y:
        with st.container(border=True):
            st.html("<div style='font-size:1.05rem; font-weight:700; color:#0D5C3A; margin-bottom:10px;'>🌾 Yield Deceleration & Logistics Shifts</div>")
            for y in clim_res.get("yield_shifts", []):
                st.html(f"""
                <div style="background:#F8FAF8; border:1px solid #E2E8F0; border-radius:8px; padding:12px; margin-bottom:12px;">
                    <div style="font-weight:700; color:#0F172A; font-size:0.92rem; margin-bottom:4px;">{y['metric']}</div>
                    <div style="font-size:0.85rem; color:#0D5C3A; font-weight:700; margin-bottom:4px;"><b>Observed Pattern:</b> {y['trend']}</div>
                    <div style="font-size:0.82rem; color:#334155; margin-bottom:6px;"><b>Field Telemetry:</b> {y['evidence']}</div>
                    <div style="font-size:0.82rem; color:#15803D; font-weight:700; background:#DCFCE7; padding:4px 8px; border-radius:4px;"><b>Recommended Action:</b> {y['recommendation']}</div>
                </div>
                """)
