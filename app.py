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

import importlib
import modules.geo_ors
import modules.explainable_ai
import modules.ui_views
importlib.reload(modules.geo_ors)
importlib.reload(modules.explainable_ai)
importlib.reload(modules.ui_views)

from modules.extended_views import (
    render_weather_intelligence_view,
    render_crop_image_quality_view,
    render_transaction_protection_view,
    render_ai_assistant_view
)
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

# Page Configuration (Hot-reload synced) (Hot-reload synced)
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

    /* Global Apple Reset & Typography */
    html, body, .stApp, [data-testid="stAppViewContainer"], .main, .block-container {
        background-color: #F5F5F7 !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Inter", "Helvetica Neue", sans-serif !important;
        color: #1D1D1F !important;
        -webkit-font-smoothing: antialiased;
    }

    /* Force Clean Apple Dark Slate on Text Elements */
    .stApp p, .stApp span, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp li {
        color: #1D1D1F !important;
    }

    /* Streamlit Main Block Padding */
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1300px !important;
    }

    /* Apple Minimal Card Containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border-radius: 18px !important;
        border: 1px solid #E5E5E7 !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.025), 0 1px 2px rgba(0, 0, 0, 0.015) !important;
        padding: 22px !important;
        transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    /* Streamlit Metric KPI Cards (Apple Style) */
    [data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E5E7 !important;
        border-radius: 16px !important;
        padding: 16px 20px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02) !important;
    }

    [data-testid="stMetricLabel"] p, [data-testid="stMetricLabel"] span {
        font-size: 0.76rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: #86868B !important;
    }

    [data-testid="stMetricValue"] div {
        font-size: 1.85rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
        color: #1D1D1F !important;
        line-height: 1.2 !important;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: #16834A !important;
    }

    /* Form Labels (Crisp & Readable) */
    label,
    label *,
    label p,
    label span,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] *,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span {
        color: #1D1D1F !important;
        -webkit-text-fill-color: #1D1D1F !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        letter-spacing: -0.01em !important;
    }

    /* Form Inputs (Apple Style: Soft Rounded 12px, Subtle Border) */
    input[type="text"], input[type="password"], input[type="number"], select, textarea,
    div[data-baseweb="input"] input,
    div[data-baseweb="input"],
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #1D1D1F !important;
        -webkit-text-fill-color: #1D1D1F !important;
        border: 1px solid #E5E5E7 !important;
        border-radius: 12px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
    }

    input:focus, div[data-baseweb="input"]:focus-within, div[data-baseweb="select"] > div:focus-within {
        border-color: #16834A !important;
        box-shadow: 0 0 0 3px rgba(22, 131, 74, 0.14) !important;
    }

    input::placeholder, textarea::placeholder {
        color: #A1A1A6 !important;
        -webkit-text-fill-color: #A1A1A6 !important;
    }

    /* Primary Apple-Green Action Buttons */
    button[kind="primary"], .stButton > button[kind="primary"] {
        background-color: #16834A !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: 1px solid #147542 !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 14.5px !important;
        padding: 9px 20px !important;
        letter-spacing: -0.01em !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 2px 6px rgba(22, 131, 74, 0.22) !important;
        transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    button[kind="primary"]:hover, .stButton > button[kind="primary"]:hover {
        background-color: #137340 !important;
        box-shadow: 0 3px 10px rgba(22, 131, 74, 0.32) !important;
        transform: translateY(-1px) !important;
    }

    /* Secondary Apple Minimal Buttons */
    button[kind="secondary"], .stButton > button:not([kind="primary"]) {
        background-color: #FFFFFF !important;
        color: #1D1D1F !important;
        -webkit-text-fill-color: #1D1D1F !important;
        border: 1px solid #E5E5E7 !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        padding: 8px 18px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
        transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    button[kind="secondary"]:hover, .stButton > button:not([kind="primary"]):hover {
        background-color: #F5F5F7 !important;
        border-color: #D1D1D6 !important;
        color: #1D1D1F !important;
        -webkit-text-fill-color: #1D1D1F !important;
        transform: translateY(-1px) !important;
    }

    /* Minimal Apple Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #FBFBFD !important;
        border-right: 1px solid #E5E5E7 !important;
        padding-top: 1rem !important;
    }

    section[data-testid="stSidebar"] * {
        color: #1D1D1F !important;
    }

    section[data-testid="stSidebar"] .stButton button[kind="primary"] {
        background-color: #DCEFE2 !important;
        color: #16834A !important;
        -webkit-text-fill-color: #16834A !important;
        border: 1px solid #B6E0C4 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        box-shadow: none !important;
        text-align: left !important;
        padding: 9px 14px !important;
    }

    section[data-testid="stSidebar"] .stButton button:not([kind="primary"]) {
        background-color: transparent !important;
        color: #1D1D1F !important;
        -webkit-text-fill-color: #1D1D1F !important;
        border: 1px solid transparent !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        box-shadow: none !important;
        text-align: left !important;
        padding: 9px 14px !important;
    }

    section[data-testid="stSidebar"] .stButton button:not([kind="primary"]):hover {
        background-color: #F0F0F3 !important;
        color: #1D1D1F !important;
    }

    /* Segmented Tabs (Apple Style) */
    div[data-baseweb="tab-list"] {
        background-color: #EFEFF2 !important;
        border-radius: 12px !important;
        padding: 4px !important;
        border: 1px solid #E5E5E7 !important;
        gap: 4px !important;
    }

    button[data-baseweb="tab"] {
        background-color: transparent !important;
        border-radius: 8px !important;
        border: none !important;
        color: #86868B !important;
        font-weight: 500 !important;
        font-size: 13.5px !important;
        padding: 6px 14px !important;
        transition: all 0.15s ease !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #1D1D1F !important;
        -webkit-text-fill-color: #1D1D1F !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
    }

    /* Stat Cards */
    .stat-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E7;
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02);
        margin-bottom: 12px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stat-card:hover {
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.05);
        transform: translateY(-1px);
    }
    .stat-label {
        font-size: 0.74rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #86868B;
        margin-bottom: 4px;
    }
    .stat-value {
        font-size: 1.85rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: #1D1D1F;
        line-height: 1.2;
    }
    .stat-subtext {
        font-size: 0.8rem;
        color: #16834A;
        font-weight: 500;
        margin-top: 4px;
    }

    /* Top Navigation Header */
    .top-nav {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E7;
        padding: 14px 24px;
        border-radius: 16px;
        margin-bottom: 22px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
    }
    .top-nav-title {
        font-size: 1.35rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        color: #1D1D1F;
    }
    .top-nav-meta {
        font-size: 0.82rem;
        color: #86868B;
        font-weight: 500;
    }

    /* Clean Table Styling */
    div[data-testid="stDataFrame"] {
        border-radius: 14px !important;
        border: 1px solid #E5E5E7 !important;
        overflow: hidden !important;
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
            # View Selector Tabs (Farmer & Commercial Buyer Portals)
            t_col1, t_col2, t_col3, t_col4 = st.columns(4)
            with t_col1:
                btn_signin_active = st.button("🔑 Sign In", use_container_width=True, type="primary" if st.session_state.auth_view == "signin" else "secondary")
                if btn_signin_active:
                    st.session_state.auth_view = "signin"
                    st.rerun()
            with t_col2:
                btn_signup_active = st.button("👨‍🌾 Farmer Join", use_container_width=True, type="primary" if st.session_state.auth_view == "signup" else "secondary")
                if btn_signup_active:
                    st.session_state.auth_view = "signup"
                    st.rerun()
            with t_col3:
                btn_buyer_active = st.button("🏢 Buyer Join", use_container_width=True, type="primary" if st.session_state.auth_view == "buyer_signup" else "secondary")
                if btn_buyer_active:
                    st.session_state.auth_view = "buyer_signup"
                    st.rerun()
            with t_col4:
                btn_forgot_active = st.button("🔒 Reset", use_container_width=True, type="primary" if st.session_state.auth_view == "forgot" else "secondary")
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

                is_dev_env = os.environ.get("KRISHI_ENV", "production").lower() == "development"
                default_email = "farmer@krishiai.com" if is_dev_env else ""
                default_pwd = "Password@123" if is_dev_env else ""
                login_email = st.text_input("Email Address", value=default_email, placeholder="name@farm.com", key="auth_email")
                login_pwd = st.text_input("Password", value=default_pwd, type="password", placeholder="Enter your secret password", key="auth_pwd")

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

                if is_dev_env:
                    st.html("""
                    <div style="text-align:center; margin: 20px 0 12px 0; border-top: 1px solid #E2E8F0; padding-top: 14px;">
                        <span style="background:#FEF3C7; color:#92400E; padding:4px 12px; border-radius:12px; font-size:0.75rem; font-weight:800; letter-spacing:0.5px;">
                            🧪 DEVELOPMENT SANDBOX TEST ACCOUNTS
                        </span>
                    </div>
                    """)
                    cd1, cd2, cd3 = st.columns(3)
                    with cd1:
                        if st.button("👨‍🌾 Test Farmer", use_container_width=True):
                            s, m, t, u = authenticate_user("farmer@krishiai.com", "Password@123", remember_me=True)
                            if s:
                                st.session_state.auth_token = t
                                st.session_state.current_user = u
                                st.rerun()
                        st.caption("Ramanagara • Sandbox")
                    with cd2:
                        if st.button("🏢 Test Buyer", use_container_width=True):
                            s, m, t, u = authenticate_user("buyer@krishiai.com", "Password@123", remember_me=True)
                            if s:
                                st.session_state.auth_token = t
                                st.session_state.current_user = u
                                st.session_state.active_nav = "Buyer Connect"
                                st.rerun()
                        st.caption("Procurement • Sandbox")
                    with cd3:
                        if st.button("🛡️ Test Admin", use_container_width=True):
                            s, m, t, u = authenticate_user("admin@krishiai.com", "Admin@123", remember_me=True)
                            if s:
                                st.session_state.auth_token = t
                                st.session_state.current_user = u
                                st.rerun()
                        st.caption("Oversight • Sandbox")

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
        <div style="padding: 8px 4px 16px 4px; border-bottom: 1px solid #E5E5E7; margin-bottom: 16px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="width:36px; height:36px; border-radius:10px; background:linear-gradient(135deg, #16834A 0%, #0D5C3A 100%); display:flex; align-items:center; justify-content:center; color:#FFFFFF; font-size:1.2rem; box-shadow:0 2px 6px rgba(22, 131, 74, 0.25);">
                    🌱
                </div>
                <div>
                    <div style="font-size:1.2rem; font-weight:700; color:#1D1D1F; letter-spacing:-0.03em; line-height:1.1;">Krishi AI</div>
                    <div style="font-size:0.72rem; color:#86868B; font-weight:500; letter-spacing:0.01em;">Intelligent Decision Platform</div>
                </div>
            </div>
        </div>
        """)

        # Minimal Apple Profile Card
        st.html(f"""
        <div style="background:#FFFFFF; border:1px solid #E5E5E7; border-radius:14px; padding:12px 14px; margin-bottom:16px; box-shadow:0 1px 3px rgba(0,0,0,0.02); display:flex; align-items:center; gap:10px;">
            <div style="width:34px; height:34px; border-radius:50%; background:#DCEFE2; color:#16834A; font-weight:700; display:flex; align-items:center; justify-content:center; font-size:0.88rem; flex-shrink:0;">
                {user['full_name'][0]}
            </div>
            <div style="overflow:hidden;">
                <div style="font-size:0.86rem; font-weight:600; color:#1D1D1F; white-space:nowrap; text-overflow:ellipsis; overflow:hidden;">{user['full_name']}</div>
                <div style="font-size:0.72rem; color:#86868B; white-space:nowrap; text-overflow:ellipsis; overflow:hidden;">📍 {farm.get('district', 'Ramanagara')}, {farm.get('state', 'Karnataka')}</div>
            </div>
        </div>
        """)

        st.html("<div style='font-size:0.7rem; font-weight:600; color:#86868B; text-transform:uppercase; letter-spacing:0.06em; margin:0 4px 8px 4px;'>Platform Modules</div>")
        role = user.get("role", "farmer")
        if role == "buyer":
            NAV_ITEMS = [
                ("📊 Buyer Command Center", "Buyer Connect"),
                ("💰 Market Intelligence", "Market Intelligence"),
                ("📈 Trend Shift Intelligence", "Trend Shift Intelligence"),
                ("🛡️ Transaction Protection", "Transaction Protection"),
                ("🤖 AI Assistant", "AI Assistant"),
                ("👤 Profile & Settings", "Settings")
            ]
        elif role == "inspector":
            NAV_ITEMS = [
                ("🔍 Inspector Quality Portal", "Crop Quality"),
                ("📋 AI Decision Reports", "AI Decision Reports"),
                ("🛡️ Transaction Protection", "Transaction Protection"),
                ("⛅ Weather Intelligence", "Weather Intelligence"),
                ("🤖 AI Assistant", "AI Assistant"),
                ("👤 Profile & Settings", "Settings")
            ]
        else:
            NAV_ITEMS = [
                ("📊 Intelligence Overview", "Intelligence Overview"),
                ("🧪 Soil & Fertilizer Advisor", "Crop Soil Advisor"),
                ("🌾 Crop Yield Prediction", "Crop Yield Prediction"),
                ("💰 Market Intelligence", "Market Intelligence"),
                ("📈 Trend Shift Intelligence", "Trend Shift Intelligence"),
                ("🤝 Buyer Marketplace", "Buyer Connect"),
                ("⚖️ Fair Price Analysis", "Anti Fraud"),
                ("📸 Crop Quality & Inspection", "Crop Quality"),
                ("⛅ Weather Intelligence", "Weather Intelligence"),
                ("🛡️ Transaction Protection", "Transaction Protection"),
                ("🤖 Gemini AI Assistant", "AI Assistant"),
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

        # APPLE MINIMAL TOP NAVIGATION BAR
    today_str = datetime.date.today().strftime("%B %d, %Y")
    st.html(f"""
    <div class="top-nav">
        <div>
            <div class="top-nav-title">{st.session_state.active_nav}</div>
            <div class="top-nav-meta">Krishi AI • Intelligent Farming Decision System • {farm.get('farm_name', 'Farm Enterprise')}</div>
        </div>
        <div style="display:flex; align-items:center; gap:12px;">
            <div style="background:#F5F5F7; border:1px solid #E5E5E7; padding:6px 14px; border-radius:20px; display:flex; align-items:center; gap:8px;">
                <span style="width:7px; height:7px; border-radius:50%; background:#16834A; display:inline-block;"></span>
                <span style="font-size:0.78rem; font-weight:600; color:#1D1D1F;">System Active</span>
                <span style="color:#D1D1D6; font-size:0.75rem;">•</span>
                <span style="font-size:0.78rem; color:#86868B;">{today_str}</span>
            </div>
            <div style="background:#FFFFFF; border:1px solid #E5E5E7; color:#16834A; font-weight:700; width:38px; height:38px; border-radius:50%; display:flex; align-items:center; justify-content:center; box-shadow:0 1px 3px rgba(0,0,0,0.03); font-size:0.88rem;">
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
    elif st.session_state.active_nav == "Crop Soil Advisor":
        render_crop_soil_advisor_view(user, farm)
    elif st.session_state.active_nav == "Anti Fraud":
        render_anti_fraud_view(user, farm)
    elif st.session_state.active_nav == "Crop Quality":
        render_crop_image_quality_view(user, farm)
    elif st.session_state.active_nav == "Weather Intelligence":
        render_weather_intelligence_view(user, farm)
    elif st.session_state.active_nav == "Transaction Protection":
        render_transaction_protection_view(user, farm)
    elif st.session_state.active_nav == "AI Assistant":
        render_ai_assistant_view(user, farm, df_market)
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
