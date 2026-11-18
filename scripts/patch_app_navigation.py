import os

target_file = os.path.join(os.path.dirname(__file__), "..", "app.py")

with open(target_file, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add imports from extended_views
import_target = "from modules.ui_views import ("
import_addition = """from modules.extended_views import (
    render_weather_intelligence_view,
    render_crop_image_quality_view,
    render_transaction_protection_view,
    render_ai_assistant_view
)
from modules.ui_views import ("""

if "render_weather_intelligence_view" not in code:
    code = code.replace(import_target, import_addition, 1)

# 2. Update NAV_ITEMS
old_nav = """        NAV_ITEMS = [
            ("📊 Intelligence Overview", "Intelligence Overview"),
            ("📜 Historical Analysis", "Historical Analysis"),
            ("🌾 Crop Yield Prediction", "Crop Yield Prediction"),
            ("💰 Market Intelligence", "Market Intelligence"),
            ("📈 Trend Shift Intelligence", "Trend Shift Intelligence"),
            ("🤝 Buyer & Industry Connect", "Buyer Connect"),
            ("⚠️ Agricultural Risk Analysis", "Agricultural Risk Analysis"),
            ("📋 AI Decision Reports", "AI Decision Reports"),
            ("👤 Profile & Settings", "Settings")
        ]"""

new_nav = """        role = user.get("role", "farmer")
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
            ]"""

code_norm = code.replace("\r\n", "\n")
old_nav_norm = old_nav.replace("\r\n", "\n")
new_nav_norm = new_nav.replace("\r\n", "\n")

if old_nav_norm in code_norm:
    code_norm = code_norm.replace(old_nav_norm, new_nav_norm, 1)

# 3. Update router
old_router = """    if st.session_state.active_nav == "Intelligence Overview":
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
        render_intelligence_overview_view(user, farm, df_market)"""

new_router = """    if st.session_state.active_nav == "Intelligence Overview":
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
        render_intelligence_overview_view(user, farm, df_market)"""

old_router_norm = old_router.replace("\r\n", "\n")
new_router_norm = new_router.replace("\r\n", "\n")

if old_router_norm in code_norm:
    code_norm = code_norm.replace(old_router_norm, new_router_norm, 1)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(code_norm)

print("SUCCESSFULLY PATCHED app.py navigation and routing!")
