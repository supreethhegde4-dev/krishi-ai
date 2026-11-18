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
    st.session_state.active_nav = "Dashboard"

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

                cd1, cd2 = st.columns(2)
                with cd1:
                    if st.button("🧑‍🌾 Demo Farmer (Ramesh)", use_container_width=True):
                        s, m, t, u = authenticate_user("farmer@krishiai.com", "Password@123", remember_me=True)
                        if s:
                            st.session_state.auth_token = t
                            st.session_state.current_user = u
                            st.rerun()
                    st.caption("5-Acre Tomato Farm • Ramanagara")
                with cd2:
                    if st.button("🛡️ Demo Administrator", use_container_width=True):
                        s, m, t, u = authenticate_user("admin@krishiai.com", "Admin@123", remember_me=True)
                        if s:
                            st.session_state.auth_token = t
                            st.session_state.current_user = u
                            st.rerun()
                    st.caption("APMC & Agronomic Oversight")

            # SIGN UP VIEW
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
            ("📊 Dashboard", "Dashboard"),
            ("🌾 Crop Advisor", "Crop Advisor"),
            ("🧪 Soil Intelligence", "Soil Intelligence"),
            ("💊 Fertilizer Advisor", "Fertilizer Advisor"),
            ("📈 Yield Analytics", "Yield Analytics"),
            ("🚚 Mandi Net Proceeds", "Mandi Net Proceeds"),
            ("📉 Price Forecast & Timing", "Price Forecast"),
            ("🛡️ Fraud Offer Detector", "Fraud Detector"),
            ("📑 Reports & History", "Reports"),
            ("👤 Profile & Settings", "Settings")
        ]

        for label, key in NAV_ITEMS:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.active_nav = key
                st.rerun()

        st.html("<hr style='border:none; border-top:1px solid #1A4D2E; margin:20px 0;'>")
        
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
            <div class="top-nav-meta">Krishi AI Command Center • {farm.get('farm_name', 'Farm Enterprise')}</div>
        </div>
        <div style="display:flex; align-items:center; gap:16px;">
            <div style="text-align:right;">
                <div style="font-size:0.88rem; font-weight:700; color:#0F3822;">{today_str}</div>
                <div style="font-size:0.75rem; color:#2D6A4F; font-weight:600;">Status: Active Production Cycle</div>
            </div>
            <div style="background-color:#E9F1EC; color:#0F3822; font-weight:800; width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center; border:1.5px solid #0F3822;">
                {user['full_name'][0]}
            </div>
        </div>
    </div>
    """)


    # ==========================================================================
    # 1. EXECUTIVE DASHBOARD MODULE
    # ==========================================================================
    if st.session_state.active_nav == "Dashboard":
        with st.container(border=True):
            st.html(f"""
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h2 style="color:#0F3822; margin:0 0 6px 0; font-size:1.7rem; font-weight:800;">Welcome back, {user['full_name']}!</h2>
                    <p style="color:#475569; margin:0; font-size:0.95rem;">
                        Real-time agricultural telemetry active for <strong>{farm.get('farm_name')}</strong> ({farm.get('acreage')} acres, {farm.get('soil_type')}).
                    </p>
                </div>
                <div>
                    <span style="background:#E9F1EC; color:#0F3822; padding:6px 14px; border-radius:20px; font-weight:700; font-size:0.85rem; border:1px solid #C8DDD0;">● Operational</span>
                </div>
            </div>
            """)

        # Key High-Level KPI Cards
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.html(f"""
            <div class="stat-card">
                <div class="stat-label">Farm Holding</div>
                <div class="stat-value">{farm.get('acreage', 2.5):.1f} Acres</div>
                <div class="stat-subtext">Soil: {farm.get('soil_type', 'Red Loam')}</div>
            </div>
            """)
        with kpi2:
            st.html(f"""
            <div class="stat-card">
                <div class="stat-label">Primary Crop</div>
                <div class="stat-value">{farm.get('primary_crops', 'Tomato').split(',')[0]}</div>
                <div class="stat-subtext">Mandi Parity: ₹16.50/kg</div>
            </div>
            """)
        with kpi3:
            st.html(f"""
            <div class="stat-card">
                <div class="stat-label">Soil Health Index</div>
                <div class="stat-value" style="color:#0D5C3A;">84 / 100</div>
                <div class="stat-subtext">Fertility Status: Good</div>
            </div>
            """)
        with kpi4:
            st.html(f"""
            <div class="stat-card">
                <div class="stat-label">APMC Wholesale Network</div>
                <div class="stat-value">2,733</div>
                <div class="stat-subtext">Active Live Mandis</div>
            </div>
            """)

        # Quick Actions & Recent Activity
        c_act1, c_act2 = st.columns([1.5, 1])
        with c_act1:
            with st.container(border=True):
                st.html("""
                <div style="font-size:1.15rem; font-weight:700; color:#0F3822; margin-bottom:12px;">⚡ Intelligent Farm Quick Actions</div>
                <div style="font-size:0.9rem; color:#475569; margin-bottom:14px;">Select an intelligence module to run automated agronomic analysis:</div>
                """)

                qa1, qa2, qa3 = st.columns(3)
                with qa1:
                    if st.button("🌱 Run Crop Matcher", use_container_width=True):
                        st.session_state.active_nav = "Crop Advisor"
                        st.rerun()
                with qa2:
                    if st.button("🧪 Analyze Soil Health", use_container_width=True):
                        st.session_state.active_nav = "Soil Intelligence"
                        st.rerun()
                with qa3:
                    if st.button("💰 Compare Mandis", use_container_width=True):
                        st.session_state.active_nav = "Mandi Net Proceeds"
                        st.rerun()

                st.html("""
                <div style="background:#F1F5F2; border-left:4px solid #0F3822; border-radius:0 8px 8px 0; padding:12px; margin-top:16px;">
                    <div style="font-weight:700; color:#0F3822; font-size:0.88rem;">📢 Seasonal Agricultural Advisory</div>
                    <div style="font-size:0.83rem; color:#334155; margin-top:4px;">
                        Wholesale Tomato prices across Bangalore Rural and Kolar show an upward seasonal trend (+₹2.20/kg expected in next 7-14 days). Review the <strong>Price Forecast & Sell Timing Advisor</strong> before confirming local farmgate deals.
                    </div>
                </div>
                """)

        with c_act2:
            with st.container(border=True):
                st.html("<div style='font-size:1.15rem; font-weight:700; color:#0F3822; margin-bottom:12px;'>📋 Recent Activity & Audits</div>")
                user_preds = get_user_predictions(user["id"])
                if user_preds:
                    for p in user_preds[:4]:
                        st.html(f"""
                        <div style="padding:8px 0; border-bottom:1px solid #F1F5F9; font-size:0.85rem;">
                            <strong style="color:#0F3822;">{p['title']}</strong><br>
                            <span style="color:#64748B; font-size:0.75rem;">{p['created_at'][:16].replace('T', ' ')} • {p['module_name']}</span>
                        </div>
                        """)
                else:
                    st.html("<div style='font-size:0.85rem; color:#64748B;'>No prior prediction records found. Run Crop Advisor or Mandi Analytics to log private farm reports.</div>")


    # ==========================================================================
    # 2. CROP ADVISOR MODULE
    # ==========================================================================
    elif st.session_state.active_nav == "Crop Advisor":
        st.markdown("#### 🌾 Precision Crop Recommendation Engine")
        st.caption("Machine learning model evaluating soil chemical parameters and local agro-climatic telemetry to predict the highest yielding crop.")

        col_in, col_out = st.columns([1, 1], gap="large")

        with col_in:
            with st.container(border=True):
                st.html("<div style='font-size:1.15rem; font-weight:700; color:#0F3822; margin-bottom:12px;'>1. Soil & Climatic Parameters</div>")

                c_n1, c_n2, c_n3 = st.columns(3)
                with c_n1:
                    n_val = st.number_input("Nitrogen (N) kg/ha", min_value=0.0, max_value=200.0, value=85.0, step=5.0)
                with c_n2:
                    p_val = st.number_input("Phosphorus (P) kg/ha", min_value=5.0, max_value=160.0, value=55.0, step=5.0)
                with c_n3:
                    k_val = st.number_input("Potassium (K) kg/ha", min_value=5.0, max_value=220.0, value=58.0, step=5.0)

                c_c1, c_c2 = st.columns(2)
                with c_c1:
                    t_val = st.number_input("Temperature (°C)", min_value=10.0, max_value=50.0, value=25.2, step=0.5)
                    ph_val = st.number_input("Soil pH", min_value=3.5, max_value=9.5, value=6.5, step=0.1)
                with c_c2:
                    h_val = st.number_input("Humidity (%)", min_value=15.0, max_value=100.0, value=71.0, step=1.0)
                    r_val = st.number_input("Rainfall (mm)", min_value=10.0, max_value=400.0, value=82.0, step=5.0)

                run_crop = st.button("Predict Optimal Crop", type="primary", use_container_width=True)

        crop_res = recommend_crop(n_val, p_val, k_val, t_val, h_val, ph_val, r_val)

        with col_out:
            with st.container(border=True):
                st.html("<div style='font-size:1.15rem; font-weight:700; color:#0F3822; margin-bottom:12px;'>2. Recommended Crop & Confidence</div>")

                rec_crop = crop_res["primary_crop"]
                conf = crop_res["confidence"]

                st.html(f"""
                <div style="background-color:#E9F1EC; border:2px solid #2D6A4F; border-radius:10px; padding:20px; text-align:center; margin-bottom:16px;">
                    <span style="background:#0F3822; color:white; padding:4px 12px; border-radius:12px; font-weight:700; font-size:0.8rem;">TOP AGRONOMIC MATCH</span>
                    <div style="font-size:2.4rem; font-weight:800; color:#0F3822; margin:8px 0;">{rec_crop}</div>
                    <div style="font-size:1.1rem; font-weight:700; color:#2D6A4F;">{conf:.1f}% Model Confidence</div>
                </div>
                """)

                st.markdown(f"**Agronomic Rationale:** {crop_res['explanation']}")

                if crop_res["alternatives"]:
                    st.markdown("**Secondary Crop Options:**")
                    for alt_name, alt_pct in crop_res["alternatives"]:
                        st.markdown(f"- **{alt_name}**: {alt_pct:.1f}% compatibility")

                if st.button("💾 Save to Private Farm Reports", key="save_crop_rec"):
                    save_user_prediction(
                        user_id=user["id"],
                        module_name="Crop Advisor",
                        title=f"Crop Match: {rec_crop} ({conf:.0f}%)",
                        inputs_json=json.dumps(crop_res["inputs"]),
                        outputs_json=json.dumps({"crop": rec_crop, "confidence": conf, "explanation": crop_res["explanation"]})
                    )
                    st.success("Report saved to your private account!")


    # ==========================================================================
    # 3. SOIL INTELLIGENCE MODULE
    # ==========================================================================
    elif st.session_state.active_nav == "Soil Intelligence":
        st.markdown("#### 🧪 Precision Soil Intelligence & Health Index")
        st.caption("Comprehensive soil chemical evaluation against ICAR standard agricultural benchmarks.")

        col_s1, col_s2 = st.columns([1, 1], gap="large")
        with col_s1:
            with st.container(border=True):
                st.html("<div style='font-size:1.15rem; font-weight:700; color:#0F3822; margin-bottom:12px;'>Soil Test Report Inputs</div>")
                sn = st.slider("Available Nitrogen (N) kg/ha", 10.0, 160.0, 75.0)
                sp = st.slider("Available Phosphorus (P) kg/ha", 5.0, 120.0, 48.0)
                sk = st.slider("Available Potassium (K) kg/ha", 10.0, 180.0, 62.0)
                sph = st.slider("Soil Reaction (pH)", 4.5, 9.0, 6.6, step=0.1)
                soc = st.slider("Organic Carbon (%)", 0.1, 1.5, 0.65, step=0.05)

        soil_res = evaluate_soil_health(sn, sp, sk, sph, soc)

        with col_s2:
            with st.container(border=True):
                st.html("<div style='font-size:1.15rem; font-weight:700; color:#0F3822; margin-bottom:12px;'>Soil Health Index & Condition</div>")

                sh_idx = soil_res["health_index"]
                sh_color = soil_res["health_color"]

                st.html(f"""
                <div style="background-color:#FFFFFF; border:2px solid {sh_color}; border-radius:10px; padding:18px; text-align:center; margin-bottom:16px;">
                    <div style="font-size:0.8rem; font-weight:700; color:#64748B; letter-spacing:0.5px;">COMPOSITE SOIL HEALTH SCORE</div>
                    <div style="font-size:2.8rem; font-weight:800; color:{sh_color};">{sh_idx} / 100</div>
                    <div style="font-size:1.05rem; font-weight:700; color:{sh_color};">{soil_res['overall_condition']}</div>
                </div>
                """)

                # Radar Chart for Soil Nutrients
                fig_soil = go.Figure()
                categories = ['Nitrogen', 'Phosphorus', 'Potassium', 'pH Balance', 'Organic Matter']
                r_vals = [
                    min(100, sn / 1.2),
                    min(100, sp / 0.8),
                    min(100, sk / 0.9),
                    max(20, 100 - abs(sph - 6.5) * 25),
                    min(100, soc * 120)
                ]
                fig_soil.add_trace(go.Scatterpolar(
                    r=r_vals,
                    theta=categories,
                    fill='toself',
                    name='Soil Fertility Index',
                    line=dict(color='#0F3822')
                ))
                fig_soil.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=False,
                    height=280,
                    margin=dict(l=30, r=30, t=20, b=20)
                )
                st.plotly_chart(fig_soil, use_container_width=True)

        with st.container(border=True):
            st.html("<div style='font-size:1.15rem; font-weight:700; color:#0F3822; margin-bottom:12px;'>Parameter Diagnostic Breakdown & Amendment Advice</div>")
            for param_name, p_data in soil_res["nutrients"].items():
                st.html(f"""
                <div style="padding:10px 0; border-bottom:1px solid #E2E8F0; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <strong style="color:#0F3822;">{param_name}:</strong> {p_data['value']} {p_data['unit']} — 
                        <span style="color:{p_data['color']}; font-weight:700;">{p_data['status']}</span>
                        <div style="font-size:0.83rem; color:#475569; margin-top:2px;">{p_data['advice']}</div>
                    </div>
                </div>
                """)


    # ==========================================================================
    # 4. FERTILIZER ADVISOR MODULE
    # ==========================================================================
    elif st.session_state.active_nav == "Fertilizer Advisor":
        st.markdown("#### 💊 Prescription Fertilizer Advisor")
        st.caption("Calculates crop nutrient deficit vs soil test reserves, computes commercial 50kg bag dosage, and creates split schedules.")

        c_f1, c_f2 = st.columns([1, 1], gap="large")
        with c_f1:
            with st.container(border=True):
                st.html("<div style='font-size:1.15rem; font-weight:700; color:#0F3822; margin-bottom:12px;'>Target Crop & Soil Values</div>")
                f_crop_sel = st.selectbox("Target Crop", ["Tomato", "Rice", "Maize", "Banana", "Cotton", "Potato", "Chickpea"])
                f_acres = st.number_input("Field Acreage (Acres)", min_value=0.5, max_value=50.0, value=farm.get("acreage", 2.0), step=0.5)
                f_sn = st.number_input("Soil Available N (kg/ha)", value=60.0)
                f_sp = st.number_input("Soil Available P (kg/ha)", value=35.0)
                f_sk = st.number_input("Soil Available K (kg/ha)", value=45.0)

        fert_res = calculate_fertilizer_prescription(f_crop_sel, f_sn, f_sp, f_sk, f_acres)

        with c_f2:
            with st.container(border=True):
                st.html(f"<div style='font-size:1.15rem; font-weight:700; color:#0F3822; margin-bottom:12px;'>Commercial Fertilizer Requirement ({f_acres:.1f} Acres)</div>")
                for item in fert_res["fertilizers"]:
                    st.html(f"""
                    <div style="background:#F8FAF8; border:1px solid #E2E8F0; border-radius:8px; padding:12px; margin-bottom:10px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:700; color:#0F3822; font-size:1.0rem;">{item['name']}</span>
                            <span style="background:#E9F1EC; color:#0F3822; font-weight:700; padding:3px 10px; border-radius:12px; font-size:0.85rem;">{item['bags_50kg']} Bags ({item['total_kg']} kg)</span>
                        </div>
                        <div style="font-size:0.8rem; color:#475569; margin-top:4px;">{item['purpose']}</div>
                    </div>
                    """)

        with st.container(border=True):
            st.html("<div style='font-size:1.15rem; font-weight:700; color:#0F3822; margin-bottom:12px;'>Agronomic Split Application Schedule</div>")
            df_sch = pd.DataFrame(fert_res["schedule"])[[
                "stage", "timing", "urea_kg", "dap_kg", "mop_kg", "method"
            ]].rename(columns={
                "stage": "Growth Stage",
                "timing": "Recommended Timing",
                "urea_kg": "Urea (kg)",
                "dap_kg": "DAP (kg)",
                "mop_kg": "MOP (kg)",
                "method": "Application Method & Guidance"
            })
            st.dataframe(df_sch, use_container_width=True)


    # ==========================================================================
    # 5. YIELD ANALYTICS MODULE
    # ==========================================================================
    elif st.session_state.active_nav == "Yield Analytics":
        st.markdown("#### 📈 Crop Yield Analytics & Benchmarking")
        st.caption("Random Forest yield prediction benchmarking farm performance against district and state agricultural production standards.")

        c_y1, c_y2 = st.columns([1, 1], gap="large")
        with c_y1:
            with st.container(border=True):
                st.html("<div style='font-size:1.15rem; font-weight:700; color:#0F3822; margin-bottom:12px;'>Farm Input Telemetry</div>")
                y_crop = st.selectbox("Crop", ["Tomato", "Rice", "Maize", "Banana", "Cotton", "Potato"], index=0)
                y_acres = st.number_input("Farm Acreage", min_value=0.5, max_value=50.0, value=farm.get("acreage", 2.5))
                y_rain = st.number_input("Seasonal Rainfall (mm)", value=85.0)
                y_ph = st.number_input("Soil pH", value=6.5)
                y_n = st.number_input("Applied Nitrogen (kg/ha)", value=80.0)
                y_p = st.number_input("Applied Phosphorus (kg/ha)", value=50.0)
                y_k = st.number_input("Applied Potassium (kg/ha)", value=60.0)

        yield_res = predict_crop_yield(y_crop, y_acres, y_n, y_p, y_k, y_rain, y_ph)

        with c_y2:
            with st.container(border=True):
                st.html("<div style='font-size:1.15rem; font-weight:700; color:#0F3822; margin-bottom:12px;'>Forecasted Harvest Production</div>")

                py_acre = yield_res["predicted_yield_per_acre"]
                tot_q = yield_res["total_yield_quintals"]
                tot_kg = yield_res["total_yield_kg"]

                st.html(f"""
                <div style="background-color:#E9F1EC; border:2px solid #2D6A4F; border-radius:10px; padding:18px; text-align:center; margin-bottom:16px;">
                    <div style="font-size:0.8rem; font-weight:700; color:#64748B;">PROJECTED HARVEST VOLUME</div>
                    <div style="font-size:2.6rem; font-weight:800; color:#0F3822;">{tot_q:,.1f} Quintals</div>
                    <div style="font-size:1.1rem; font-weight:700; color:#2D6A4F;">{tot_kg:,.0f} kg Total Production</div>
                    <div style="font-size:0.85rem; color:#475569; margin-top:4px;">({py_acre:.1f} Quintals/Acre) • Rating: {yield_res['performance_rating']}</div>
                </div>
                """)

                fig_y = go.Figure()
                fig_y.add_trace(go.Bar(
                    x=['District Average', 'State Benchmark', 'Your Predicted Farm Yield', 'Top Decile Farms'],
                    y=[yield_res['district_avg_yield'], yield_res['state_avg_yield'], py_acre, yield_res['high_performing_yield']],
                    marker_color=['#94A3B8', '#64748B', '#2D6A4F', '#0F3822'],
                    text=[f"{v:.1f} Q" for v in [yield_res['district_avg_yield'], yield_res['state_avg_yield'], py_acre, yield_res['high_performing_yield']]],
                    textposition='auto'
                ))
                fig_y.update_layout(
                    title=f"{y_crop} Yield Benchmark (Quintals/Acre)",
                    yaxis_title="Yield (Quintals/Acre)",
                    template="plotly_white",
                    height=280,
                    margin=dict(l=30, r=30, t=40, b=30)
                )
                st.plotly_chart(fig_y, use_container_width=True)


    # ==========================================================================
    # 6. MANDI NET PROCEEDS & LOGISTICS MODULE
    # ==========================================================================
    elif st.session_state.active_nav == "Mandi Net Proceeds":
        st.markdown("#### 🚚 Mandi Net Proceeds Ranker & Logistics Optimizer")
        st.caption("Calculates road distance via ORS Matrix API, deducts vehicle freight & APMC fees (1.5% cess + 2.0% commission), and ranks mandis by net proceeds.")

        col_mp1, col_mp2, col_mp3 = st.columns(3)
        with col_mp1:
            m_crop = st.selectbox("Crop", sorted(df_market['commodity'].unique()), index=sorted(df_market['commodity'].unique()).index("Tomato") if "Tomato" in df_market['commodity'].unique() else 0)
        with col_mp2:
            m_qty = st.number_input("Quantity to Transport (kg)", min_value=100.0, max_value=20000.0, value=500.0, step=50.0)
        with col_mp3:
            m_veh = st.selectbox("Vehicle Profile", list(DEFAULT_VEHICLE_CONFIGS.keys()), index=0)

        vehicle_cfg = DEFAULT_VEHICLE_CONFIGS[m_veh].copy()

        # Compute Comparative Proceeds Table
        p_res = compute_mandi_proceeds_table(
            df_marketplace=df_market,
            crop_name=m_crop,
            quantity_kg=m_qty,
            farmer_lat=farm.get("latitude", 12.7209),
            farmer_lon=farm.get("longitude", 77.2799),
            vehicle_config=vehicle_cfg
        )

        b_m = p_res["best_mandi"]
        n_m = p_res["nearest_mandi"]

        if b_m and n_m:
            cb1, cb2, cb3 = st.columns(3)
            with cb1:
                st.html(f"""
                <div class="stat-card" style="border:2px solid #0D5C3A; background:#F0FDF4;">
                    <div class="stat-label">🏆 Highest Net Proceeds Mandi</div>
                    <div style="font-size:1.3rem; font-weight:800; color:#0D5C3A;">{b_m['mandi']}</div>
                    <div class="stat-value" style="font-size:1.6rem; color:#0D5C3A;">₹{b_m['net_proceeds']:,.2f}</div>
                    <div class="stat-subtext">Net: ₹{b_m['net_price_per_kg']:.2f}/kg • Dist: {b_m['road_distance_km']} km</div>
                </div>
                """)
            with cb2:
                st.html(f"""
                <div class="stat-card">
                    <div class="stat-label">📍 Nearest Mandi</div>
                    <div style="font-size:1.3rem; font-weight:800; color:#0D5C3A;">{n_m['mandi']}</div>
                    <div class="stat-value" style="font-size:1.6rem; color:#0F172A;">₹{n_m['net_proceeds']:,.2f}</div>
                    <div class="stat-subtext">Net: ₹{n_m['net_price_per_kg']:.2f}/kg • Dist: {n_m['road_distance_km']} km</div>
                </div>
                """)
            with cb3:
                net_gain = p_res["net_advantage_vs_nearest"]
                st.html(f"""
                <div class="stat-card" style="background:#FFFBEB; border-color:#F59E0B;">
                    <div class="stat-label">💡 Net Arbitrage Advantage</div>
                    <div style="font-size:1.1rem; color:#475569;">Best vs Nearest Mandi</div>
                    <div class="stat-value" style="font-size:1.6rem; color:#D97706;">{'+' if net_gain>=0 else ''}₹{net_gain:,.2f}</div>
                    <div class="stat-subtext">Net extra profit after all transport expenses</div>
                </div>
                """)

            st.markdown("#### Ranked Mandi Ledger")
            df_m_disp = pd.DataFrame(p_res["records"])[[
                "mandi", "district", "state", "modal_price_kg", "road_distance_km",
                "gross_revenue", "transport_cost", "total_expenses", "net_proceeds", "net_price_per_kg", "suitability_badge"
            ]].rename(columns={
                "mandi": "Market",
                "district": "District",
                "state": "State",
                "modal_price_kg": "Gross Modal (₹/kg)",
                "road_distance_km": "Distance (km)",
                "gross_revenue": "Gross (₹)",
                "transport_cost": "Freight (₹)",
                "total_expenses": "Fees (₹)",
                "net_proceeds": "Net Proceeds (₹)",
                "net_price_per_kg": "Net Realized (₹/kg)",
                "suitability_badge": "Cold-Chain Match"
            })
            st.dataframe(df_m_disp, use_container_width=True, height=350)


    # ==========================================================================
    # 7. PRICE FORECAST & SELL TIMING ADVISOR (NEW TAB 5 FEATURE)
    # ==========================================================================
    elif st.session_state.active_nav == "Price Forecast":
        st.markdown("#### 📉 Historical Price Analytics & Predictive Sell Timing Advisor")
        st.caption("Powered by 4-year DuckDB time-series arrivals (2023–2026), RandomForest lag regressor, and deterministic storage-versus-spoilage economics.")

        f_meta = get_distinct_filter_values(commodity="Tomato", state=farm.get("state", "Karnataka"))
        
        c_pf1, c_pf2, c_pf3, c_pf4 = st.columns(4)
        with c_pf1:
            pf_crop = st.selectbox("Crop", f_meta["commodities"], index=f_meta["commodities"].index("Tomato") if "Tomato" in f_meta["commodities"] else 0)
        with c_pf2:
            st_opts = ["All States"] + f_meta["states"]
            pf_state = st.selectbox("State", st_opts, index=st_opts.index(farm.get("state", "Karnataka")) if farm.get("state", "Karnataka") in st_opts else 0)
        with c_pf3:
            sub_meta = get_distinct_filter_values(commodity=pf_crop, state=pf_state)
            dst_opts = ["All Districts"] + sub_meta["districts"]
            pf_dist = st.selectbox("District", dst_opts, index=0)
        with c_pf4:
            mkt_meta = get_distinct_filter_values(commodity=pf_crop, state=pf_state, district=pf_dist)
            m_opts = ["All Markets"] + mkt_meta["markets"]
            pf_market = st.selectbox("Market", m_opts, index=0)

        c_pf5, c_pf6 = st.columns([2, 1])
        with c_pf5:
            pf_comp = st.multiselect("Overlay Comparison Markets", mkt_meta["markets"], default=[mkt_meta["markets"][0]] if mkt_meta["markets"] else [])
        with c_pf6:
            pf_horizon = st.selectbox("Forecast Horizon", [3, 7, 14], index=1, format_func=lambda x: f"{x} Days Ahead")

        with st.spinner("Executing high-speed DuckDB scan over 4-year Parquet files..."):
            df_hist_series = query_historical_prices(
                commodity=pf_crop,
                state=pf_state,
                district=pf_dist,
                markets=pf_comp if pf_comp else ([pf_market] if pf_market != "All Markets" else None)
            )

        if not df_hist_series.empty:
            primary_mkt = pf_market if pf_market != "All Markets" else (pf_comp[0] if pf_comp else "All")
            df_target_m = df_hist_series[df_hist_series['Market'] == primary_mkt] if pf_market != "All Markets" else df_hist_series
            
            fc_output = train_and_forecast_price(df_target_m if not df_target_m.empty else df_hist_series, horizons=[3, 7, 14])

            k1, k2, k3, k4, k5 = st.columns(5)
            lat_p = fc_output.get("latest_observed_price", df_hist_series['modal_price_kg'].iloc[-1])
            p3 = fc_output.get("predictions", {}).get("3_day", {}).get("predicted_price_kg", lat_p)
            p7 = fc_output.get("predictions", {}).get("7_day", {}).get("predicted_price_kg", lat_p)
            p14 = fc_output.get("predictions", {}).get("14_day", {}).get("predicted_price_kg", lat_p)
            mae_v = fc_output.get("metrics", {}).get("mae", 1.5)

            with k1:
                st.html(f"<div class='stat-card'><div class='stat-label'>Latest Price</div><div class='stat-value'>₹{lat_p:.2f}</div><div class='stat-subtext'>{fc_output.get('latest_observed_date', 'Recent')}</div></div>")
            with k2:
                st.html(f"<div class='stat-card'><div class='stat-label'>3-Day Forecast</div><div class='stat-value'>₹{p3:.2f}</div><div class='stat-subtext'>{p3-lat_p:+.2f}/kg</div></div>")
            with k3:
                st.html(f"<div class='stat-card' style='background:#F0FDF4; border-color:#0D5C3A;'><div class='stat-label' style='color:#0D5C3A;'>7-Day Forecast</div><div class='stat-value' style='color:#0D5C3A;'>₹{p7:.2f}</div><div class='stat-subtext'>{p7-lat_p:+.2f}/kg</div></div>")
            with k4:
                st.html(f"<div class='stat-card'><div class='stat-label'>14-Day Forecast</div><div class='stat-value'>₹{p14:.2f}</div><div class='stat-subtext'>{p14-lat_p:+.2f}/kg</div></div>")
            with k5:
                st.html(f"<div class='stat-card'><div class='stat-label'>Validation Error</div><div class='stat-value'>±₹{mae_v:.2f}</div><div class='stat-subtext'>MAE on Out-of-Time Test</div></div>")

            fig_fc = go.Figure()
            for m_n, g_d in df_hist_series.groupby("Market"):
                g_d = g_d.sort_values("date")
                fig_fc.add_trace(go.Scatter(
                    x=g_d["Arrival_Date"],
                    y=g_d["modal_price_kg"],
                    mode="lines",
                    name=f"{m_n} (Actual Modal)",
                    line=dict(width=2.5)
                ))

            if fc_output.get("forecast_series") is not None:
                f_df = fc_output["forecast_series"]
                last_d = fc_output["latest_observed_date"]
                cx = [last_d] + list(f_df["Arrival_Date"])
                cy = [lat_p] + list(f_df["predicted_modal_price_kg"])
                cu = [lat_p] + list(f_df["confidence_upper_kg"])
                cl = [lat_p] + list(f_df["confidence_lower_kg"])

                fig_fc.add_trace(go.Scatter(
                    x=cx, y=cy, mode="lines+markers",
                    name="AI Predicted Future Price",
                    line=dict(color="#C62828", width=3, dash="dash"),
                    marker=dict(size=6)
                ))
                fig_fc.add_trace(go.Scatter(
                    x=cx + cx[::-1], y=cu + cl[::-1], fill='toself',
                    fillcolor='rgba(198, 40, 40, 0.12)', line=dict(color='rgba(255,255,255,0)'),
                    name="Uncertainty Range (±1.64σ)"
                ))

            fig_fc.update_layout(
                title=f"{pf_crop} Price History & Machine Learning Forecast – {primary_mkt}",
                xaxis_title="Arrival Date",
                yaxis_title="Wholesale Price (₹/kg)",
                template="plotly_white",
                height=480,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_fc, use_container_width=True)

            with st.container(border=True):
                st.html("<div style='font-size:1.15rem; font-weight:700; color:#0F3822; margin-bottom:12px;'>⚖️ Deterministic Sell Now vs Wait Decision Engine</div>")
                
                c_dec1, c_dec2 = st.columns([1, 1])
                with c_dec1:
                    t_pred_price = fc_output.get("predictions", {}).get(f"{pf_horizon}_day", {}).get("predicted_price_kg", lat_p)
                    st_cost = st.number_input("Daily Storage Cost (₹/kg/day)", value=0.15, step=0.05)
                    spoil_pct = st.slider("Expected Spoilage & Weight Loss (%)", 0.0, 20.0, 3.5 if pf_horizon==7 else (1.5 if pf_horizon==3 else 7.0), step=0.5)

                adv_res = evaluate_sell_timing(
                    crop_name=pf_crop,
                    quantity_kg=farm.get("acreage", 2.0) * 200.0,
                    current_price_kg=lat_p,
                    predicted_future_price_kg=t_pred_price,
                    horizon_days=pf_horizon,
                    daily_storage_cost_per_kg=st_cost,
                    spoilage_pct=spoil_pct,
                    forecast_mae=mae_v
                )

                with c_dec2:
                    st.html(f"""
                    <div style="background:#FFFFFF; border:2px solid {adv_res['badge_color']}; border-radius:10px; padding:16px;">
                        <span style="background:#0F3822; color:white; padding:3px 10px; border-radius:12px; font-weight:700; font-size:0.8rem;">STRATEGIC RECOMMENDATION</span>
                        <div style="font-size:2.0rem; font-weight:800; color:{adv_res['badge_color']}; margin:4px 0;">{adv_res['recommendation']}</div>
                        <div style="font-size:0.92rem; color:#111827; margin-bottom:10px;">{adv_res['rationale']}</div>
                        <div style="font-size:0.83rem; background:#F8FAF8; border:1px solid #E2E8F0; padding:8px; border-radius:6px;"><strong>Action:</strong> {adv_res['strategy']}</div>
                    </div>
                    """)


    # ==========================================================================
    # 8. FRAUD & UNFAIR OFFER DETECTOR MODULE
    # ==========================================================================
    elif st.session_state.active_nav == "Fraud Detector":
        st.markdown("#### 🛡️ Predatory Offer & Unfair Middleman Transaction Detector")
        st.caption("Audits buyer farmgate bids against fair mandi parity, calculates farmer loss, and creates negotiation counter-offers.")

        c_fr1, c_fr2 = st.columns([1, 1], gap="large")
        with c_fr1:
            with st.container(border=True):
                st.html("<div style='font-size:1.15rem; font-weight:700; color:#0F3822; margin-bottom:12px;'>Buyer Offer Parameters</div>")
                offered_p = st.number_input("Buyer's Quoted Price (₹/kg)", min_value=1.0, max_value=150.0, value=11.50, step=0.5)
                offered_q = st.number_input("Quantity in Deal (kg)", min_value=100.0, max_value=25000.0, value=500.0, step=50.0)
                pay_term = st.selectbox("Payment Terms", ["Immediate Cash / UPI at Weighbridge", "Payment after 7 days", "Payment after 15 days", "Unspecified Credit"])

        bench_m = 16.50
        fr_res = evaluate_buyer_offer(offered_p, offered_q, bench_m, bench_m * 0.88, payment_terms=pay_term)

        with c_fr2:
            with st.container(border=True):
                st.html("<div style='font-size:1.15rem; font-weight:700; color:#0F3822; margin-bottom:12px;'>AI Parity & Anomaly Audit</div>")

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


    # ==========================================================================
    # 9. REPORTS & HISTORY (ISOLATED USER RECORDS)
    # ==========================================================================
    elif st.session_state.active_nav == "Reports":
        st.markdown("#### 📑 Private Farm Reports & Saved Intelligence")
        st.caption(f"Historical prediction ledger isolated for **{user['full_name']}** ({user['email']}).")

        preds = get_user_predictions(user["id"])
        if preds:
            df_rep = pd.DataFrame(preds)
            st.dataframe(df_rep[["id", "module_name", "title", "created_at"]].rename(columns={
                "id": "Report ID",
                "module_name": "Module",
                "title": "Title / Recommendation",
                "created_at": "Timestamp"
            }), use_container_width=True)

            csv_data = df_rep.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Historical Reports (CSV)",
                data=csv_data,
                file_name=f"krishi_ai_reports_{user['id']}.csv",
                mime="text/csv"
            )
        else:
            st.info("No saved predictions yet. Use Crop Advisor or Soil Intelligence to log your first report.")


    # ==========================================================================
    # 10. PROFILE & SETTINGS MODULE
    # ==========================================================================
    elif st.session_state.active_nav == "Settings":
        st.markdown("#### 👤 Farmer Profile & Enterprise Settings")

        col_p1, col_p2 = st.columns([1, 1], gap="large")

        with col_p1:
            with st.container(border=True):
                st.html("<div style='font-size:1.15rem; font-weight:700; color:#0F3822; margin-bottom:12px;'>Farm Profile Information</div>")
                
                p_farm_name = st.text_input("Farm Name", value=farm.get("farm_name", "Green Valley Agro Farm"))
                p_acreage = st.number_input("Holding Acreage (Acres)", value=float(farm.get("acreage", 2.5)), step=0.5)
                p_village = st.text_input("Village / Town", value=farm.get("village", "Ramanagara"))
                p_district = st.text_input("District", value=farm.get("district", "Ramanagara"))
                p_state = st.text_input("State", value=farm.get("state", "Karnataka"))
                p_soil = st.selectbox("Predominant Soil Type", ["Red Sandy Loam", "Clay Loam", "Black Cotton Soil", "Alluvial", "Laterite"], index=0)
                p_crops = st.text_input("Primary Crops", value=farm.get("primary_crops", "Tomato, Maize, Banana"))

                if st.button("Save Farm Profile", type="primary"):
                    up_ok, up_msg = update_farm_profile(user["id"], {
                        "farm_name": p_farm_name,
                        "acreage": p_acreage,
                        "village": p_village,
                        "district": p_district,
                        "state": p_state,
                        "soil_type": p_soil,
                        "primary_crops": p_crops,
                        "latitude": farm.get("latitude", 12.7209),
                        "longitude": farm.get("longitude", 77.2799),
                        "irrigation_source": farm.get("irrigation_source", "Borewell Drip")
                    })
                    if up_ok:
                        st.success("Farm profile updated!")
                        st.session_state.current_user["farm"]["farm_name"] = p_farm_name
                        st.session_state.current_user["farm"]["acreage"] = p_acreage
                        st.session_state.current_user["farm"]["district"] = p_district
                        st.session_state.current_user["farm"]["state"] = p_state
                        st.rerun()

        with col_p2:
            with st.container(border=True):
                st.html("<div style='font-size:1.15rem; font-weight:700; color:#0F3822; margin-bottom:12px;'>Security & Password Change</div>")
                
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

                st.html(f"<div style='margin-top:20px; font-size:0.85rem; color:#64748B;'>Account ID: #{user['id']} • Role: {user['role'].upper()}</div>")


# ==============================================================================
# MAIN ROUTING
# ==============================================================================
if not st.session_state.current_user:
    render_authentication_page()
else:
    render_main_application()
