"""
Krishi AI – Intelligent Farming Decision System
Commercial-Grade AgriTech SaaS Platform
Includes:
- Complete User Authentication: Sign In, Sign Up, Remember Me, Rate Limiting, Forgot Password, Data Isolation
- High-Contrast Modern AgriTech Command Center UI/UX:
  Primary: Deep Forest Green (#0F3822), Secondary: Natural Green (#2D6A4F), Background: Warm Off-White (#F8FAF8)
- 10 Enterprise Agronomic Modules:
  1. Executive Dashboard (Farm Overview, Live Health, Quick Insights)
  2. Crop Advisor (ML Recommendation based on N-P-K, Temperature, Humidity, pH, Rainfall)
  3. Soil Intelligence (Nutrient Gauges, pH Balance, Health Index, Organic Amendments)
  4. Fertilizer Advisor (Crop NPK Deficit, Urea/DAP/MOP Bag Calculation, 3-Stage Split Schedule)
  5. Yield Analytics (Harvest Forecasting, Benchmarks, State Comparison)
  6. Mandi Net Proceeds & Logistics (APMC Ranking, ORS Road Routing, Normal vs Cold-Chain)
  7. Price Forecast & Sell Timing Advisor (DuckDB 4-Year Parquet Analytics, Plotly Interactive Forecast, Sell Now vs Wait Engine)
  8. Fraud & Unfair Offer Detector (Predatory Bid Anomaly Detection, Farmer Loss, Negotiation Script)
  9. Reports & Audits (User-Isolated Prediction History, Parameter Review, CSV Export)
  10. Profile & Settings (Farm Profile Configuration, Password Management, Session Logout)
"""
import os
import sys
import json
import datetime
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Modules
from modules.auth_db import (
    register_user, authenticate_user, get_user_by_session_token,
    invalidate_session, create_password_reset_token, reset_password_with_token,
    change_user_password, update_farm_profile, save_user_prediction,
    get_user_predictions
)
from modules.data_loader import inspect_marketplace_data, load_normalized_marketplace_data
from modules.geo_ors import geocode_address, get_directions_route, load_coordinates_cache
from modules.transport_engine import DEFAULT_VEHICLE_CONFIGS, calculate_transport_cost, check_temperature_suitability
from modules.proceeds_calculator import compute_mandi_proceeds_table, DEFAULT_MANDI_FEES
from modules.quality_evaluator import evaluate_quality
from modules.fair_price_model import predict_fair_price_band
from modules.fraud_detector import evaluate_buyer_offer
from modules.historical_data import (
    get_distinct_filter_values, query_historical_prices, ensure_historical_parquet_available
)
from modules.forecasting import train_and_forecast_price
from modules.sell_advisor import evaluate_sell_timing
from modules.crop_advisor import recommend_crop
from modules.soil_intelligence import evaluate_soil_health
from modules.fertilizer_advisor import calculate_fertilizer_prescription
from modules.yield_analytics import predict_crop_yield

# New Predictive Intelligence & Decision Modules
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

# High-Contrast Dedicated UI Views
from modules.buyer_connect_db import init_buyer_connect_tables
from modules.buyer_ui_view import render_buyer_connect_view

# Initialize Buyer & Industry Connect Tables
init_buyer_connect_tables()

from modules.ui_views import (
    render_intelligence_overview_view,
    render_historical_analysis_view,
    render_crop_yield_view,
    render_market_intelligence_view,
    render_seasonal_intelligence_view,
    render_risk_analysis_view,
    render_what_if_view,
    render_explainable_ai_view,
    render_decision_reports_view,
    render_crop_soil_advisor_view,
    render_anti_fraud_view,
    render_settings_view,
    render_trend_shift_view
)

# Page Configuration
st.set_page_config(
    page_title="Krishi AI – Intelligent Farming Decision System",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# High-Contrast Commercial AgriTech SaaS Theme CSS
st.html("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    /* Global Viewport Background & Base Reset */
    html, body, .stApp, [data-testid="stAppViewContainer"], .main, .block-container {
        background-color: #F8FAF8 !important;
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #0F172A !important;
    }

    /* Force Dark Slate Text on All Text Elements */
    .stApp p, .stApp span, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp li {
        color: #0F172A !important;
    }

    /* ALL Streamlit Widget Labels (Emails, Passwords, Numbers, Selectboxes) */
    label,
    label *,
    label p,
    label span,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] *,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span,
    [data-testid="stMarkdownContainer"] p,
    .stTextInput label,
    .stTextInput label p,
    .stNumberInput label,
    .stNumberInput label p,
    .stSelectbox label,
    .stSelectbox label p,
    .stSlider label,
    .stSlider label p,
    .stCheckbox label,
    .stCheckbox label p,
    .stCheckbox label span,
    .stCheckbox span {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        font-weight: 700 !important;
        font-size: 0.93rem !important;
        letter-spacing: -0.1px !important;
    }

    /* Form Inputs (Text, Password, Numbers, Select) */
    input[type="text"], input[type="password"], input[type="number"], select, textarea,
    div[data-baseweb="input"] input,
    div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
        font-size: 14.5px !important;
        font-weight: 500 !important;
    }

    input:focus, div[data-baseweb="input"]:focus-within {
        border-color: #0D5C3A !important;
        box-shadow: 0 0 0 3px rgba(13, 92, 58, 0.12) !important;
    }

    /* Input Placeholders */
    input::placeholder, textarea::placeholder {
        color: #94A3B8 !important;
        -webkit-text-fill-color: #94A3B8 !important;
        opacity: 1 !important;
    }

    /* Primary Action Buttons (Sign In, Create, Calculate) */
    button[kind="primary"], .stButton > button[kind="primary"] {
        background-color: #0D5C3A !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: 1px solid #0A4D30 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 9px 20px !important;
        box-shadow: 0 2px 5px rgba(13, 92, 58, 0.22) !important;
        transition: all 0.2s ease !important;
    }

    button[kind="primary"]:hover, .stButton > button[kind="primary"]:hover {
        background-color: #0A4D30 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(13, 92, 58, 0.35) !important;
        transform: translateY(-1px) !important;
    }

    /* Secondary / Demo Buttons (NO MORE BLACK BOXES) */
    button[kind="secondary"], .stButton > button:not([kind="primary"]) {
        background-color: #F0FDF4 !important;
        color: #14532D !important;
        -webkit-text-fill-color: #14532D !important;
        border: 1.5px solid #86EFAC !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        padding: 8px 16px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
        transition: all 0.2s ease !important;
    }

    button[kind="secondary"]:hover, .stButton > button:not([kind="primary"]):hover {
        background-color: #DCFCE7 !important;
        border-color: #22C55E !important;
        color: #0F3822 !important;
        -webkit-text-fill-color: #0F3822 !important;
        box-shadow: 0 3px 8px rgba(34, 197, 94, 0.18) !important;
        transform: translateY(-1px) !important;
    }

    /* Card Containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border-radius: 14px !important;
        border: 1.5px solid #E2E8F0 !important;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04) !important;
        padding: 22px !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #072715 !important;
        border-right: 1px solid #144426 !important;
    }

    section[data-testid="stSidebar"] * {
        color: #F1F5F2 !important;
    }

    section[data-testid="stSidebar"] label[data-testid="stWidgetLabel"] p {
        color: #B5D1BD !important;
        font-weight: 600 !important;
    }

    section[data-testid="stSidebar"] .stButton button {
        background-color: #0E361D !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: 1px solid #1E5C35 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }

    section[data-testid="stSidebar"] .stButton button:hover {
        background-color: #1A542F !important;
        border-color: #34D399 !important;
    }

    /* KPI Stat Cards */
    .stat-card {
        background-color: #FFFFFF;
        border: 1.5px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 10px;
    }
    .stat-label {
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748B;
        margin-bottom: 4px;
    }
    .stat-value {
        font-size: 1.65rem;
        font-weight: 800;
        color: #0D5C3A;
        line-height: 1.2;
    }
    .stat-subtext {
        font-size: 0.82rem;
        color: #15803D;
        font-weight: 600;
        margin-top: 4px;
    }

    /* Top Navigation Header */
    .top-nav {
        background-color: #FFFFFF;
        border: 1.5px solid #E2E8F0;
        padding: 14px 24px;
        border-radius: 10px;
        margin-bottom: 22px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    }
    .top-nav-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0D5C3A;
    }
    .top-nav-meta {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 500;
    }
</style>
""")


# Session State Initialization
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "auth_view" not in st.session_state:
    st.session_state.auth_view = "signin"  # 'signin', 'signup', 'forgot'
if "active_nav" not in st.session_state:
    st.session_state.active_nav = "Intelligence Overview"

# Verify Existing Session
if st.session_state.auth_token and not st.session_state.current_user:
    validated_user = get_user_by_session_token(st.session_state.auth_token)
    if validated_user:
        st.session_state.current_user = validated_user
    else:
        st.session_state.auth_token = None


# Cached Data Loaders
@st.cache_data
def get_cached_marketplace():
    return load_normalized_marketplace_data()

df_market = get_cached_marketplace()


# ==============================================================================
# AUTHENTICATION SCREEN: CENTERED PREMIUM AGRITECH SAAS PORTAL (PART 1 & PART 3)
# ==============================================================================
def render_authentication_page():
    # Centered Header
    st.html("""
    <div style="text-align:center; padding: 24px 0 16px 0;">
        <div style="display:inline-flex; align-items:center; gap:8px; background:#DCFCE7; border:1.5px solid #86EFAC; padding:6px 18px; border-radius:24px; margin-bottom:12px;">
            <span style="font-size:1.15rem;">🌿</span>
            <span style="font-size:0.85rem; font-weight:800; color:#14532D; letter-spacing:0.5px;">KRISHI AI • ENTERPRISE AGRITECH PLATFORM</span>
        </div>
        <h1 style="color:#0D5C3A; font-size:2.4rem; font-weight:800; margin:0 0 8px 0; letter-spacing:-0.5px;">
            Intelligent Farming Decision System
        </h1>
        <p style="color:#475569; font-size:1.02rem; max-width:680px; margin:0 auto; line-height:1.5;">
            Commercial-grade agricultural intelligence for modern farm enterprises: ML crop matching, soil chemistry telemetry, APMC mandi logistics & predictive price timing.
        </p>
    </div>
    """)

    # Center column for authentication card
    _, col_card, _ = st.columns([1, 1.4, 1])

    with col_card:
        with st.container(border=True):
            # View Selector Tabs
            t_col1, t_col2, t_col3 = st.columns(3)
            with t_col1:
                btn_signin_active = st.button("🔑 Sign In", use_container_width=True, type="primary" if st.session_state.auth_view == "signin" else "secondary")
                if btn_signin_active:
                    st.session_state.auth_view = "signin"
                    st.rerun()
            with t_col2:
                btn_signup_active = st.button("✨ Create Account", use_container_width=True, type="primary" if st.session_state.auth_view == "signup" else "secondary")
                if btn_signup_active:
                    st.session_state.auth_view = "signup"
                    st.rerun()
            with t_col3:
                btn_forgot_active = st.button("🔒 Reset Token", use_container_width=True, type="primary" if st.session_state.auth_view == "forgot" else "secondary")
                if btn_forgot_active:
                    st.session_state.auth_view = "forgot"
                    st.rerun()

            st.html("<div style='height: 10px;'></div>")

            # SIGN IN VIEW
            if st.session_state.auth_view == "signin":
                st.html("""
                <div style="margin-bottom: 14px;">
                    <h3 style="color:#0D5C3A; font-size:1.35rem; font-weight:800; margin:0 0 2px 0;">Sign In to Your Account</h3>
                    <div style="color:#64748B; font-size:0.88rem;">Enter your verified credentials to access your farm portal</div>
                </div>
                """)

                login_email = st.text_input("Email Address", value="farmer@krishiai.com", placeholder="name@farm.com", key="auth_email")
                login_pwd = st.text_input("Password", value="Password@123", type="password", key="auth_pwd")

                c_rem, c_fgt = st.columns([1, 1])
                with c_rem:
                    remember_me = st.checkbox("Remember me (30 days)", value=True)
                with c_fgt:
                    st.html("""
                    <div style="text-align:right; padding-top:6px;">
                        <span style="color:#64748B; font-size:0.83rem;">Forgot password? Click <strong>Reset Token</strong> tab</span>
                    </div>
                    """)

                if st.button("Sign In to Account →", type="primary", use_container_width=True):
                    if not login_email or not login_pwd:
                        st.error("Please enter both email address and password.")
                    else:
                        with st.spinner("Verifying credentials..."):
                            success, msg, token, user_data = authenticate_user(login_email, login_pwd, remember_me=remember_me)
                            if success:
                                st.session_state.auth_token = token
                                st.session_state.current_user = user_data
                                st.success("Welcome back! Loading Command Center...")
                                st.rerun()
                            else:
                                st.error(msg)

                st.html("""
                <div style="text-align:center; margin: 20px 0 12px 0; border-top: 1px solid #E2E8F0; padding-top: 14px;">
                    <span style="background:#F1F5F9; color:#475569; padding:4px 12px; border-radius:12px; font-size:0.75rem; font-weight:800; letter-spacing:0.5px;">
                        ⚡ 1-CLICK INSTANT DEMO ACCESS
                    </span>
                </div>
                """)

                cd1, cd2, cd3 = st.columns(3)
                with cd1:
                    if st.button("👨‍🌾 Demo Farmer (Ramesh)", use_container_width=True):
                        s, m, t, u = authenticate_user("farmer@krishiai.com", "Password@123", remember_me=True)
                        if s:
                            st.session_state.auth_token = t
                            st.session_state.current_user = u
                            st.rerun()
                    st.caption("5-Acre Tomato Farm • Ramanagara")
                with cd2:
                    if st.button("🏢 Demo Buyer (ITC Agro)", use_container_width=True):
                        s, m, t, u = authenticate_user("buyer@krishiai.com", "Password@123", remember_me=True)
                        if s:
                            st.session_state.auth_token = t
                            st.session_state.current_user = u
                            st.session_state.active_nav = "Buyer Connect"
                            st.rerun()
                    st.caption("Industrial Procurement Hub")
                with cd3:
                    if st.button("🛡️ Demo Administrator", use_container_width=True):
                        s, m, t, u = authenticate_user("admin@krishiai.com", "Admin@123", remember_me=True)
                        if s:
                            st.session_state.auth_token = t
                            st.session_state.current_user = u
                            st.rerun()
                    st.caption("APMC & Agronomic Oversight")

            elif st.session_state.auth_view == "signup":
                st.html("""
                <div style="margin-bottom: 14px;">
                    <h3 style="color:#0D5C3A; font-size:1.35rem; font-weight:800; margin:0 0 2px 0;">Create Farmer Account</h3>
                    <div style="color:#64748B; font-size:0.88rem;">Configure your private, tenant-isolated agricultural system</div>
                </div>
                """)

                su_name = st.text_input("Full Name", placeholder="e.g. Ramesh Gowda")
                su_email = st.text_input("Email Address", placeholder="name@farm.com")
                su_phone = st.text_input("Phone Number (Optional)", placeholder="+91 98450 12345")
                su_pwd = st.text_input("Create Password", type="password", help="Minimum 8 characters with an uppercase letter and a number")
                su_pwd_conf = st.text_input("Confirm Password", type="password")
                su_agree = st.checkbox("I accept the Krishi AI Terms of Service and Privacy Policy")

                if st.button("Create My Account →", type="primary", use_container_width=True):
                    if not su_name or not su_email or not su_pwd:
                        st.error("Please fill in all required fields.")
                    elif not su_agree:
                        st.error("Please accept the Terms of Service to continue.")
                    elif su_pwd != su_pwd_conf:
                        st.error("Passwords do not match. Please re-enter carefully.")
                    else:
                        with st.spinner("Configuring isolated farm database..."):
                            ok_r, msg_r = register_user(su_name, su_email, su_pwd, su_phone, role="farmer")
                            if ok_r:
                                st.success(msg_r)
                                st.session_state.auth_view = "signin"
                                st.rerun()
                            else:
                                st.error(msg_r)

            # FORGOT PASSWORD VIEW
            else:
                st.html("""
                <div style="margin-bottom: 14px;">
                    <h3 style="color:#0D5C3A; font-size:1.35rem; font-weight:800; margin:0 0 2px 0;">Account Recovery</h3>
                    <div style="color:#64748B; font-size:0.88rem;">Generate a single-use secure reset token</div>
                </div>
                """)

                fgt_email = st.text_input("Registered Email Address", placeholder="name@farm.com")
                if st.button("Generate Recovery Token", use_container_width=True):
                    if not fgt_email:
                        st.error("Please enter your registered email address.")
                    else:
                        tok_ok, tok_msg, gen_token = create_password_reset_token(fgt_email)
                        if tok_ok and gen_token:
                            st.success("Recovery token generated successfully!")
                            st.info(f"🔑 **Your Reset Token:** `{gen_token}`")
                        else:
                            st.warning(tok_msg)

                st.html("<div style='margin: 16px 0 6px 0; font-weight:700; color:#0D5C3A;'>Reset Password with Token</div>")
                in_token = st.text_input("Reset Token", placeholder="Paste token here")
                in_new_pwd = st.text_input("New Password", type="password")

                if st.button("Update Password →", type="primary", use_container_width=True):
                    if not in_token or not in_new_pwd:
                        st.error("Please provide both token and new password.")
                    else:
                        rst_ok, rst_msg = reset_password_with_token(in_token, in_new_pwd)
                        if rst_ok:
                            st.success(rst_msg)
                            st.session_state.auth_view = "signin"
                            st.rerun()
                        else:
                            st.error(rst_msg)

    # 4 Bottom Feature Highlights
    st.html("""
    <div style="max-width:1050px; margin: 32px auto 16px auto;">
        <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:14px;">
            <div style="background:#FFFFFF; border:1.5px solid #E2E8F0; border-radius:10px; padding:14px; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
                <div style="font-size:1.3rem; margin-bottom:4px;">🌾</div>
                <div style="font-weight:700; font-size:0.92rem; color:#0D5C3A;">Precision Agronomy</div>
                <div style="font-size:0.78rem; color:#64748B; margin-top:2px;">ML crop matching, soil health index & NPK advice</div>
            </div>
            <div style="background:#FFFFFF; border:1.5px solid #E2E8F0; border-radius:10px; padding:14px; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
                <div style="font-size:1.3rem; margin-bottom:4px;">🚚</div>
                <div style="font-weight:700; font-size:0.92rem; color:#0D5C3A;">Mandi Logistics</div>
                <div style="font-size:0.78rem; color:#64748B; margin-top:2px;">ORS routing, cold-chain parity & net proceed ranking</div>
            </div>
            <div style="background:#FFFFFF; border:1.5px solid #E2E8F0; border-radius:10px; padding:14px; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
                <div style="font-size:1.3rem; margin-bottom:4px;">📈</div>
                <div style="font-weight:700; font-size:0.92rem; color:#0D5C3A;">Price Forecasting</div>
                <div style="font-size:0.78rem; color:#64748B; margin-top:2px;">4-year DuckDB lag models & Sell Now vs Wait advice</div>
            </div>
            <div style="background:#FFFFFF; border:1.5px solid #E2E8F0; border-radius:10px; padding:14px; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
                <div style="font-size:1.3rem; margin-bottom:4px;">🛡️</div>
                <div style="font-weight:700; font-size:0.92rem; color:#0D5C3A;">Anti-Fraud Parity</div>
                <div style="font-size:0.78rem; color:#64748B; margin-top:2px;">Predatory quote detection & counter-negotiations</div>
            </div>
        </div>
        <div style="text-align:center; margin-top:20px; font-size:0.8rem; color:#64748B;">
            🔒 <strong>Bank-Grade Security:</strong> Argon2id/bcrypt password hashing • 100% Tenant Isolation • Zero Plain-Text Storage
        </div>
    </div>
    """)


# ==============================================================================
# MAIN PROTECTED APPLICATION DASHBOARD (PART 4, 5, 6)
# ==============================================================================
def render_main_application():
    user = st.session_state.current_user
    farm = user.get("farm", {})

    # LEFT SIDEBAR NAVIGATION
    with st.sidebar:
        st.html("""
        <div style="padding: 10px 0 16px 0; border-bottom: 1px solid #1A4D2E; margin-bottom: 16px;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:1.4rem;">🌿</span>
                <span style="font-size:1.3rem; font-weight:800; color:#FFFFFF; letter-spacing:-0.5px;">Krishi AI</span>
            </div>
            <div style="font-size:0.75rem; color:#A4B6A6; margin-top:2px; font-weight:600;">INTELLIGENT FARMING SYSTEM</div>
        </div>
        """)

        # Farmer / Farm Profile Badge
        st.html(f"""
        <div style="background-color:#143F24; border:1px solid #235C37; border-radius:8px; padding:12px; margin-bottom:16px;">
            <div style="font-size:0.9rem; font-weight:700; color:#FFFFFF;">{user['full_name']}</div>
            <div style="font-size:0.8rem; color:#C2DEC9;">{farm.get('farm_name', 'My Farm')}</div>
            <div style="font-size:0.75rem; color:#85B892; margin-top:2px;">📍 {farm.get('district', 'Ramanagara')}, {farm.get('state', 'Karnataka')}</div>
        </div>
        """)

        st.html("<div style='font-size:0.75rem; font-weight:700; color:#85B892; text-transform:uppercase; margin-bottom:8px;'>SYSTEM MODULES</div>")
        
        NAV_ITEMS = [
            ("📊 Intelligence Overview", "Intelligence Overview"),
            ("📜 Historical Analysis", "Historical Analysis"),
            ("🌾 Crop Yield Prediction", "Crop Yield Prediction"),
            ("💰 Market Intelligence", "Market Intelligence"),
            ("📈 Trend Shift Intelligence", "Trend Shift Intelligence"),
            ("🤝 Buyer & Industry Connect", "Buyer Connect"),
            ("⚠️ Agricultural Risk Analysis", "Agricultural Risk Analysis"),
            ("📋 AI Decision Reports", "AI Decision Reports"),
            ("👤 Profile & Settings", "Settings")
        ]

        for label, key in NAV_ITEMS:
            btn_type = "primary" if st.session_state.active_nav == key else "secondary"
            if st.button(label, key=f"nav_{key}", use_container_width=True, type=btn_type):
                st.session_state.active_nav = key
                st.rerun()

        st.html("<hr style='border:none; border-top:1px solid #1A4D2E; margin:16px 0;'>")
        
        # Logout Button
        if st.button("🚪 Logout Active Session", use_container_width=True):
            invalidate_session(st.session_state.auth_token)
            st.session_state.auth_token = None
            st.session_state.current_user = None
            st.rerun()

    # TOP NAVIGATION BAR
    today_str = datetime.date.today().strftime("%B %d, %Y")
    st.html(f"""
    <div class="top-nav">
        <div>
            <div class="top-nav-title">{st.session_state.active_nav}</div>
            <div class="top-nav-meta">Krishi AI Decision Platform • {farm.get('farm_name', 'Farm Enterprise')}</div>
        </div>
        <div style="display:flex; align-items:center; gap:16px;">
            <div style="text-align:right;">
                <div style="font-size:0.88rem; font-weight:700; color:#0D5C3A;">{today_str}</div>
                <div style="font-size:0.75rem; color:#15803D; font-weight:600;">Status: Predictive Intelligence Engine Active</div>
            </div>
            <div style="background-color:#E9F1EC; color:#0D5C3A; font-weight:800; width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center; border:1.5px solid #0D5C3A;">
                {user['full_name'][0]}
            </div>
        </div>
    </div>
    """)

    # ROUTING TO DEDICATED HIGH-CONTRAST UI VIEWS
    if st.session_state.active_nav == "Intelligence Overview":
        render_intelligence_overview_view(user, farm, df_market)
    elif st.session_state.active_nav == "Historical Analysis":
        render_historical_analysis_view(user, farm)
    elif st.session_state.active_nav == "Crop Yield Prediction":
        render_crop_yield_view(user, farm)
    elif st.session_state.active_nav == "Market Intelligence":
        render_market_intelligence_view(user, farm, df_market)
    elif st.session_state.active_nav == "Trend Shift Intelligence":
        render_trend_shift_view(user, farm, df_market)
    elif st.session_state.active_nav == "Buyer Connect":
        render_buyer_connect_view(user, farm, df_market)
    elif st.session_state.active_nav == "Agricultural Risk Analysis":
        render_risk_analysis_view(user, farm)
    elif st.session_state.active_nav == "AI Decision Reports":
        render_decision_reports_view(user, farm, df_market)
    elif st.session_state.active_nav == "Settings":
        render_settings_view(user, farm)
    else:
        render_intelligence_overview_view(user, farm, df_market)


# ==============================================================================
# MAIN ROUTING
# ==============================================================================
if not st.session_state.current_user:
    render_authentication_page()
else:
    render_main_application()
