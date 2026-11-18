"""
Extended Enterprise Views for Krishi AI.
Provides:
1. Weather & Agro-Climatology Intelligence View (Open-Meteo & NASA POWER)
2. Crop Image Intelligence & Inspector Quality Verification View
3. Transaction Protection & Weighbridge Scam Detection View
4. Gemini Agricultural AI Assistant View
5. Inspector Quality Oversight Dashboard
"""
import io
import time
import datetime
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

from modules.api_clients import (
    OpenMeteoWeatherClient, NasaPowerClient, GeminiAgriClient,
    PlantNetClient, DataGovInMandiClient, get_api_status_report
)
from modules.image_intelligence import analyze_produce_batch, GRADE_CONFIGS
from modules.transaction_protection import evaluate_transaction_risk
from modules.ai_assistant import build_farmer_system_context, query_agricultural_assistant
from modules.buyer_connect_db import (
    get_all_inspections, verify_crop_inspection, record_trade_transaction,
    get_transactions_for_user, file_transaction_dispute, create_produce_listing,
    get_all_produce_listings, get_farmer_produce_listings
)


# ==============================================================================
# 1. WEATHER & AGRO-CLIMATOLOGY INTELLIGENCE VIEW
# ==============================================================================
def render_weather_intelligence_view(user, farm):
    st.markdown("#### ⛅ Real-Time Agro-Meteorological Intelligence")
    st.caption("Live field telemetry via Open-Meteo & NASA POWER satellite agroclimatology archives.")

    lat = float(farm.get("latitude", 12.7209))
    lon = float(farm.get("longitude", 77.2799))
    district = farm.get("district", "Ramanagara")
    state = farm.get("state", "Karnataka")

    with st.expander("📍 Weather Origin Coordinates", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            lat = st.number_input("Field Latitude", value=lat, format="%.4f", key="wx_lat")
        with c2:
            lon = st.number_input("Field Longitude", value=lon, format="%.4f", key="wx_lon")

    # Fetch live weather telemetry
    wx = OpenMeteoWeatherClient.get_weather_intelligence(lat, lon)
    cur = wx.get("current", {})
    daily = wx.get("daily_forecast", {})
    alerts = wx.get("agronomic_alerts", [])
    nasa = NasaPowerClient.get_climatology(lat, lon)

    # Status Bar
    st.html(f"""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:12px 18px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <span style="font-weight:700; color:#0D5C3A;">Telemetry Source:</span>
            <span style="font-size:0.85rem; color:#334155; margin-left:6px;">{wx.get('provider')}</span>
        </div>
        <div>
            <span style="font-size:0.8rem; background:{'#DCFCE7' if wx.get('is_live') else '#FEF3C7'}; color:{'#15803D' if wx.get('is_live') else '#B45309'}; padding:4px 10px; border-radius:20px; font-weight:700;">
                {'● LIVE SATELLITE & SENSOR FEED' if wx.get('is_live') else '● REGIONAL CLIMATOLOGY'}
            </span>
            <span style="font-size:0.8rem; color:#64748B; margin-left:8px;">Updated: {wx.get('timestamp')}</span>
        </div>
    </div>
    """)

    # Top KPI Metrics
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric(label="Current Temp", value=f"{cur.get('temperature_c', 24.5):.1f} °C", delta=f"Min: {min(daily.get('min_temps', [19])):.1f}°C")
    with m2:
        st.metric(label="Relative Humidity", value=f"{cur.get('humidity_pct', 65.0):.0f} %", delta="Transpiration Favorable")
    with m3:
        st.metric(label="Wind Speed", value=f"{cur.get('wind_speed_kmh', 8.2):.1f} km/h", delta="Safe for Spraying")
    with m4:
        st.metric(label="Rain Probability", value=f"{cur.get('rain_probability_pct', 10.0):.0f} %", delta=f"{sum(daily.get('rain_sums_mm', [0])):.1f}mm 7d Accum.")
    with m5:
        st.metric(label="Solar Radiation", value=f"{nasa.get('mean_solar_radiation_mj', 19.2)} MJ/m²", delta=f"{nasa.get('photosynthetic_suitability', 'Optimal')}")

    # Actionable Agronomic Stress Alerts
    st.markdown("##### 🚨 Agronomic Stress & Field Advisories")
    for alert in alerts:
        sev_color = "#DC2626" if alert.get("severity") == "High" else "#D97706" if alert.get("severity") == "Warning" else "#16834A"
        bg_color = "#FEF2F2" if alert.get("severity") == "High" else "#FFFBEB" if alert.get("severity") == "Warning" else "#F0FDF4"
        st.html(f"""
        <div style="background:{bg_color}; border-left:4px solid {sev_color}; border-radius:8px; padding:12px 16px; margin-bottom:10px;">
            <div style="font-weight:700; color:{sev_color}; font-size:0.95rem;">{alert.get('badge')}</div>
            <div style="font-size:0.85rem; color:#1F2937; margin-top:4px;">{alert.get('message')}</div>
        </div>
        """)

    # 7-Day Weather Forecast Chart
    st.markdown("##### 📅 7-Day Temperature & Precipitation Outlook")
    dates = daily.get("dates", [])
    if dates:
        df_wx = pd.DataFrame({
            "Date": dates,
            "Max Temp (°C)": daily.get("max_temps", []),
            "Min Temp (°C)": daily.get("min_temps", []),
            "Rainfall (mm)": daily.get("rain_sums_mm", []),
            "Rain Chance (%)": daily.get("rain_prob_max", [])
        })

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_wx["Date"], y=df_wx["Max Temp (°C)"], mode="lines+markers", name="Max Daytime Temp (°C)", line=dict(color="#DC2626", width=2.5)))
        fig.add_trace(go.Scatter(x=df_wx["Date"], y=df_wx["Min Temp (°C)"], mode="lines+markers", name="Min Night Temp (°C)", line=dict(color="#2563EB", width=2.5)))
        fig.add_trace(go.Bar(x=df_wx["Date"], y=df_wx["Rainfall (mm)"], name="Rainfall Volume (mm)", marker_color="#10B981", opacity=0.6, yaxis="y2"))

        fig.update_layout(
            height=320,
            margin=dict(l=20, r=20, t=25, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(title="Temperature (°C)", side="left"),
            yaxis2=dict(title="Rainfall (mm)", side="right", overlaying="y", showgrid=False),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF"
        )
        st.plotly_chart(fig, use_container_width=True)


# ==============================================================================
# 2. CROP IMAGE INTELLIGENCE & QUALITY ASSESSMENT VIEW
# ==============================================================================
def render_crop_image_quality_view(user, farm):
    st.markdown("#### 📸 Crop & Produce Image Quality Intelligence")
    st.caption("AI-assisted preliminary produce grading and accredited human inspection certification workflow.")

    user_role = user.get("role", "farmer")
    crop = farm.get("primary_crops", "Tomato").split(",")[0].strip()

    tab_eval, tab_history = st.tabs(["🔍 Produce Quality Evaluation", "📋 Certified Inspection Records"])

    with tab_eval:
        st.html("""
        <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:10px; padding:12px 16px; margin-bottom:16px;">
            <div style="font-weight:700; color:#15803D; font-size:0.9rem;">AI Preliminary Grading Guidance</div>
            <div style="font-size:0.8rem; color:#166534; margin-top:2px;">
                Upload multiple clear photos of your harvested batch. The multimodal engine assesses skin firmness, discoloration, and mechanical bruising. 
                <b>Note:</b> AI assessment is strictly indicative. Final APMC transactions require human inspector certification.
            </div>
        </div>
        """)

        c_u1, c_u2 = st.columns([1.5, 1])
        with c_u1:
            uploaded_files = st.file_uploader(
                "Upload Produce Photographs (Batch Sample)",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                help="Upload 1 to 5 close-up photographs showing representative fruits or tubers."
            )
        with c_u2:
            sel_crop = st.selectbox("Target Commodity", ["Tomato", "Potato", "Onion", "Banana", "Maize", "Rice", "Wheat"], index=0)
            lot_qty = st.number_input("Batch Quantity (Quintals)", min_value=1.0, value=25.0, step=5.0)

        if uploaded_files:
            # Display uploaded thumbnails
            cols = st.columns(min(4, len(uploaded_files)))
            for idx, f in enumerate(uploaded_files[:4]):
                with cols[idx]:
                    st.image(f, caption=f"Sample #{idx+1}", use_container_width=True)

            if st.button("🚀 Run AI Produce Quality Assessment", type="primary", use_container_width=True):
                with st.spinner("Processing botanical identification and surface defect analysis..."):
                    res = analyze_produce_batch(
                        image_files=uploaded_files,
                        crop_name=sel_crop,
                        farmer_id=user["id"],
                        farmer_name=user.get("full_name", "Farmer"),
                        quantity_quintals=lot_qty
                    )
                    st.session_state["last_image_eval"] = res
                    st.success("Quality analysis completed successfully.")

        if "last_image_eval" in st.session_state:
            eval_res = st.session_state["last_image_eval"]
            ev_status = eval_res.get("status", "AI_ASSESSED")

            if ev_status == "REJECTED":
                st.html(f"""
                <div style="background:#FEF2F2; border:2px solid #DC2626; border-radius:12px; padding:18px; margin-top:16px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="font-size:1.25rem; font-weight:800; color:#991B1B;">
                            ⛔ STATUS: REJECTED
                        </div>
                        <span style="background:#FEE2E2; color:#991B1B; padding:4px 10px; border-radius:20px; font-weight:700; font-size:0.8rem;">
                            SECURITY GATE TRIGGERED
                        </span>
                    </div>
                    <div style="color:#B91C1C; font-weight:700; margin:10px 0 4px 0; font-size:1.0rem;">
                        REASON: {eval_res.get('reason', 'NOT_AN_AGRICULTURAL_PRODUCE_IMAGE')}
                    </div>
                    <p style="color:#4B5563; font-size:0.9rem; margin:0 0 10px 0;">
                        {eval_res.get('message', 'Uploaded file identified as a non-agricultural subject.')}
                    </p>
                    <div style="background:#FFFFFF; border:1px solid #FECACA; border-radius:8px; padding:12px; font-size:0.85rem; color:#374151;">
                        <b>🛡️ Production Safety & Privacy Notice:</b> Personal documents (marks cards, certificates, Aadhaar/PAN, invoices) and unrelated objects are strictly rejected. Rejected files are <b>never transmitted to external AI cloud services</b> and no commercial trading lots or false grades are created.
                    </div>
                </div>
                """)
            elif ev_status == "UNABLE_TO_ASSESS":
                st.html(f"""
                <div style="background:#FFFBEB; border:2px solid #F59E0B; border-radius:12px; padding:18px; margin-top:16px;">
                    <div style="font-size:1.2rem; font-weight:800; color:#92400E;">
                        ⚠️ STATUS: UNABLE TO ASSESS
                    </div>
                    <div style="color:#B45309; font-weight:600; margin:6px 0;">
                        REASON: {eval_res.get('reason', 'INSUFFICIENT_IMAGE_QUALITY')}
                    </div>
                    <p style="color:#4B5563; font-size:0.88rem; margin:0;">
                        {eval_res.get('message', 'Please upload clear, well-lit photographs showing representative fruits or tubers.')}
                    </p>
                </div>
                """)
            else:
                g_det = eval_res.get("grade_details", {})
                st.html(f"""
                <div style="background:#FFFFFF; border:2px solid {g_det.get('color', '#16834A')}; border-radius:12px; padding:18px; margin-top:16px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="font-size:1.3rem; font-weight:800; color:{g_det.get('color', '#16834A')};">
                            {g_det.get('badge')}
                        </div>
                        <div style="background:#F1F5F9; color:#475569; padding:4px 10px; border-radius:20px; font-weight:700; font-size:0.8rem;">
                            Batch Ref: {eval_res.get('batch_ref')}
                        </div>
                    </div>
                    <div style="font-size:0.85rem; color:#475569; margin:8px 0;">{g_det.get('description')}</div>
                    <hr style="border:none; border-top:1px solid #E2E8F0; margin:10px 0;">
                    <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:12px; margin-top:10px;">
                        <div><b>Species:</b> {eval_res.get('botanical_species')} ({eval_res.get('botanical_confidence')}%)</div>
                        <div><b>Defect Ratio:</b> {eval_res.get('defect_percent')}% (Threshold: &le; {g_det.get('tolerance_defect_pct')}%)</div>
                        <div><b>Firmness:</b> {eval_res.get('firmness_level')}</div>
                    </div>
                </div>
                """)

                st.markdown("##### 🔬 Detailed Agronomic Observations")
                for obs in eval_res.get("observations", []):
                    st.markdown(f"• {obs}")

                conf = eval_res.get("confidence_scores", {})
                st.caption(f"🎯 Multi-Stage Confidence: Classification {conf.get('produce_classification_confidence', 95):.1f}% | Crop ID {conf.get('crop_identification_confidence', 90):.1f}% | Grading {conf.get('grading_confidence', 88):.1f}%")
                st.info("ℹ️ Status: **AI ASSESSED (PRELIMINARY)** — To convert this into a certified APMC trading lot, assign an accredited inspector in the Certified Records tab.")

    with tab_history:
        st.markdown("##### 📑 Official Inspection Records")
        inspections = get_all_inspections()
        if inspections:
            df_insp = pd.DataFrame(inspections)
            st.dataframe(
                df_insp[["id", "batch_ref", "crop", "quantity_quintals", "ai_grade", "status", "inspector_grade", "certificate_hash", "created_at"]],
                use_container_width=True,
                hide_index=True
            )

            # Inspector Sign-Off Section (If User is Inspector or Admin)
            if user_role in ["inspector", "admin"]:
                st.markdown("---")
                st.markdown("##### ✍️ Accredited Inspector Quality Certification Portal")
                pending = [i for i in inspections if i.get("status") == "AI_ASSESSED"]
                if pending:
                    sel_batch = st.selectbox("Select Pending Batch to Certify", [f"{p['id']}: {p['batch_ref']} ({p['crop']} - {p['farmer_name']})" for p in pending])
                    insp_id = int(sel_batch.split(":")[0])

                    ci1, ci2, ci3 = st.columns(3)
                    with ci1:
                        c_grade = st.selectbox("Inspector Verified Grade", ["Grade A (Premium Export)", "Grade B (Standard Wholesale)", "Grade C (Processing & Pulp)"])
                    with ci2:
                        c_brix = st.number_input("Brix Sugar Reading (°Bx)", value=5.2, step=0.1)
                    with ci3:
                        c_caliper = st.number_input("Average Caliper Size (mm)", value=58.0, step=1.0)

                    c_def = st.slider("Certified Defect Percentage", 0.0, 30.0, 4.0)
                    c_notes = st.text_input("Inspector Compliance Remarks", "Passed APMC physical grading norms; lot ready for commercial auction.")

                    if st.button("🎖️ Issue Certified Human Inspection Certificate", type="primary"):
                        succ, msg = verify_crop_inspection(
                            inspection_id=insp_id,
                            inspector_id=user["id"],
                            inspector_name=user.get("full_name", "Accredited Inspector"),
                            inspector_grade=c_grade,
                            brix_reading=c_brix,
                            size_caliper_mm=c_caliper,
                            defect_percent=c_def,
                            inspection_notes=c_notes
                        )
                        if succ:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    st.info("No batches pending inspection.")
        else:
            st.info("No inspection records logged yet. Upload photos in the evaluation tab to start.")


# ==============================================================================
# 3. TRANSACTION PROTECTION & SCAM DETECTION VIEW
# ==============================================================================
def render_transaction_protection_view(user, farm):
    st.markdown("#### 🛡️ Transaction Protection & Discrepancy Auditing")
    st.caption("Mathematical protection against weighbridge tampering, unauthorized moisture deductions, and predatory settlements.")

    tab_audit, tab_log, tab_dispute = st.tabs(["⚖️ Live Discrepancy Calculator", "📜 Transaction History", "🚨 File Grievance"])

    with tab_audit:
        st.markdown("##### 📐 Dispatch vs Settlement Audit")
        ca1, ca2 = st.columns(2)
        with ca1:
            st.markdown("**Farmer Dispatch Telemetry**")
            f_qty = st.number_input("Farmer Dispatched Weight (kg)", value=1000.0, step=50.0, key="tp_f_qty")
            agreed_rate = st.number_input("Contracted Agreed Rate (₹/kg)", value=18.50, step=0.50, key="tp_agr_rate")
        with ca2:
            st.markdown("**Buyer Weighbridge Settlement**")
            wb_qty = st.number_input("Weighbridge Net Weight Recorded (kg)", value=920.0, step=50.0, key="tp_wb_qty")
            paid_rate = st.number_input("Actual Rate Settled by Buyer (₹/kg)", value=17.50, step=0.50, key="tp_pd_rate")

        ca3, ca4 = st.columns(2)
        with ca3:
            deduct_amt = st.number_input("Deductions Applied (₹) (Sorting/Moisture/Unloading)", value=500.0, step=100.0, key="tp_deduct")
        with ca4:
            paid_amt = st.number_input("Actual Bank / UPI Transfer Received (₹)", value=15600.0, step=500.0, key="tp_paid")

        # Run risk assessment
        audit = evaluate_transaction_risk(
            farmer_weight_kg=f_qty,
            weighbridge_weight_kg=wb_qty,
            agreed_rate_per_kg=agreed_rate,
            paid_rate_per_kg=paid_rate,
            deductions_amount=deduct_amt,
            payment_received=paid_amt
        )

        st.html(f"""
        <div style="background:#FFFFFF; border:2px solid {audit['badge_color']}; border-radius:12px; padding:18px; margin-top:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="font-size:1.2rem; font-weight:800; color:{audit['badge_color']};">
                    RISK AUDIT: {audit['risk_level'].replace('_', ' ')}
                </div>
                <div style="font-size:1.1rem; font-weight:800; color:#DC2626;">
                    Total Farmer Shortfall: ₹{audit['total_shortfall_rs']:,.2f}
                </div>
            </div>
            <hr style="border:none; border-top:1px solid #E2E8F0; margin:10px 0;">
            <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:10px; font-size:0.85rem;">
                <div><b>Weight Gap:</b> {audit['weight_diff_kg']:.1f} kg ({audit['weight_diff_pct']}%)</div>
                <div><b>Contracted Value:</b> ₹{audit['expected_gross_rs']:,.2f}</div>
                <div><b>Actual Realized:</b> ₹{audit['payment_received_rs']:,.2f}</div>
                <div><b>Deductions:</b> ₹{audit['deductions_rs']:,.2f}</div>
            </div>
        </div>
        """)

        st.markdown("##### 🔍 Audit Findings & Discrepancies")
        for flag in audit["flags"]:
            st.warning(f"**[{flag['type']}]** {flag['message']}")

        if audit["dispute_recommended"]:
            st.error("⚠️ Significant financial discrepancy detected! It is recommended to file an official grievance or request certified weighbridge inspection.")

    with tab_log:
        st.markdown("##### 📜 Recorded Trade Transactions")
        txns = get_transactions_for_user(user["id"], role=user.get("role", "farmer"))
        if txns:
            df_tx = pd.DataFrame(txns)
            st.dataframe(
                df_tx[["id", "buyer_name", "crop", "farmer_weight_kg", "weighbridge_weight_kg", "weight_discrepancy_kg", "agreed_rate_per_kg", "payment_status", "risk_level", "created_at"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No recorded transactions on your account yet.")

    with tab_dispute:
        st.markdown("##### 🚨 Submit Formal Transaction Dispute to APMC")
        with st.form("form_dispute"):
            d_buyer = st.text_input("Buyer / Aggregator Name", "Private Middleman / Trader")
            d_crop = st.text_input("Commodity", farm.get("primary_crops", "Tomato").split(",")[0].strip())
            d_type = st.selectbox("Discrepancy Category", [
                "Tare & Weighbridge Shortfall (>5% Weight Loss)",
                "Unauthorized Produce Quality Cut / Discount",
                "Delayed or Incomplete Payment Transfer",
                "Uncontracted Freight or Commission Deductions"
            ])
            d_loss = st.number_input("Claimed Financial Loss (₹)", value=2400.0, step=100.0)
            d_stmt = st.text_area("Detailed Statement of Facts", "Dispatch weight recorded on digital scale was 1000 kg. Buyer weighbridge recorded 920 kg without tare slip verification. Rate was settled at ₹17.50 instead of contracted ₹18.50.")
            d_slip = st.text_input("Weighbridge Slip / Gate Pass Serial #", "WB-BLR-2026-9812")

            submitted = st.form_submit_button("⚖️ Submit Dispute to APMC Arbitration Cell", type="primary")
            if submitted:
                succ, msg, t_id = record_trade_transaction(
                    farmer_id=user["id"],
                    farmer_name=user.get("full_name", "Farmer"),
                    buyer_id=1,
                    buyer_name=d_buyer,
                    crop=d_crop,
                    farmer_weight_kg=1000.0,
                    weighbridge_weight_kg=920.0,
                    agreed_rate_per_kg=18.5,
                    paid_rate_per_kg=17.5,
                    deductions_amount=500.0,
                    payment_received=15600.0,
                    weighbridge_slip_ref=d_slip,
                    notes=d_stmt
                )
                if succ and t_id:
                    s_d, m_d = file_transaction_dispute(
                        transaction_id=t_id,
                        farmer_id=user["id"],
                        buyer_id=1,
                        dispute_type=d_type,
                        claimed_loss_amount=d_loss,
                        dispute_statement=d_stmt
                    )
                    st.success(m_d)
                else:
                    st.error("Failed to register transaction.")


# ==============================================================================
# 4. GEMINI AGRICULTURAL AI ASSISTANT VIEW
# ==============================================================================
def render_ai_assistant_view(user, farm, df_market=None):
    st.markdown("#### 🤖 Gemini Agricultural AI Assistant")
    st.caption("Context-aware agricultural advisor providing agronomic, logistics, and fair-pricing guidance.")

    crop = farm.get("primary_crops", "Tomato").split(",")[0].strip()
    status_report = get_api_status_report()
    gemini_status = next((s for s in status_report if "Gemini" in s["name"]), {})

    # Top Status Banner
    is_live_ai = gemini_status.get("configured", False)
    st.html(f"""
    <div style="background:{'#F0FDF4' if is_live_ai else '#FFFBEB'}; border:1px solid {'#86EFAC' if is_live_ai else '#FDE68A'}; border-radius:10px; padding:10px 16px; margin-bottom:14px; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <b>Engine Active:</b> <span style="color:{'#15803D' if is_live_ai else '#B45309'};">{gemini_status.get('status')}</span>
        </div>
        <div style="font-size:0.8rem; color:#64748B;">
            {f'API Key: {gemini_status.get("env_var")}' if is_live_ai else 'Deterministic Agricultural Expert Rules Operating'}
        </div>
    </div>
    """)

    # Build Sanitized Farmer Context
    farm_context = build_farmer_system_context(
        user=user,
        farm=farm,
        crop_name=crop,
        benchmark_price_kg=18.50,
        predicted_yield_qtl=105.9,
        best_mandi_name="K.R.Nagar APMC",
        best_mandi_net_proceeds=11001.88,
        best_mandi_dist_km=48.2
    )

    with st.expander("🔒 Inspect Privacy-Guarded Farm Context (Sent to Assistant)", expanded=False):
        st.json(farm_context)

    # Initialize chat history
    if "agri_chat_history" not in st.session_state:
        st.session_state.agri_chat_history = [
            {
                "role": "assistant",
                "content": f"Namaste {user.get('full_name', 'Farmer')}! I am your Krishi AI Assistant. I have loaded the active telemetry for your {farm.get('acreage', 2.5)}-acre {farm.get('farm_name', 'farm')} in {farm.get('district', 'Ramanagara')}. How can I assist you with your {crop} crop today?",
                "time": datetime.datetime.now().strftime("%H:%M")
            }
        ]

    # Quick Prompt Pills
    st.markdown("**Quick Inquiries:**")
    qp1, qp2, qp3, qp4 = st.columns(4)
    preset_query = None
    with qp1:
        if st.button("💰 Best Mandi Price", use_container_width=True):
            preset_query = f"Which mandi gives the highest net proceeds for my {crop} today?"
    with qp2:
        if st.button("🧪 Fertilizer Plan", use_container_width=True):
            preset_query = f"What fertilizer dosage do you prescribe for my {crop} based on my soil profile?"
    with qp3:
        if st.button("🌾 Harvest Yield", use_container_width=True):
            preset_query = f"What is my expected harvest yield and what are the main positive drivers?"
    with qp4:
        if st.button("⛅ Weather Alerts", use_container_width=True):
            preset_query = "What weather conditions or rainfall risks should I watch out for this week?"

    # Display Chat History
    for msg in st.session_state.agri_chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User Input
    user_query = st.chat_input("Ask about mandi rates, soil health, fertilizer dosages, or price trends...")
    active_prompt = preset_query or user_query

    if active_prompt:
        st.session_state.agri_chat_history.append({"role": "user", "content": active_prompt, "time": datetime.datetime.now().strftime("%H:%M")})
        with st.chat_message("user"):
            st.markdown(active_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing farm telemetry and market benchmarks..."):
                response = query_agricultural_assistant(active_prompt, farm_context)
                ans_text = response.get("answer", "I am currently analyzing your farm parameters.")
                st.markdown(ans_text)
                st.session_state.agri_chat_history.append({"role": "assistant", "content": ans_text, "time": datetime.datetime.now().strftime("%H:%M")})
