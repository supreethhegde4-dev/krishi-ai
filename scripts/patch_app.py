import os

app_path = "app.py"
with open(app_path, "r", encoding="utf-8") as f:
    content = f.read()

start_marker = "        NAV_ITEMS = ["
end_marker = "# ==============================================================================\n# MAIN ROUTING"

idx_start = content.find(start_marker)
idx_end = content.find(end_marker)

if idx_start == -1 or idx_end == -1:
    print(f"Error: Markers not found! Start: {idx_start}, End: {idx_end}")
    exit(1)

new_dispatcher = '''        NAV_ITEMS = [
            ("📊 Intelligence Overview", "Intelligence Overview"),
            ("📜 Historical Analysis", "Historical Analysis"),
            ("🌾 Crop Yield Prediction", "Crop Yield Prediction"),
            ("💰 Market Intelligence", "Market Intelligence"),
            ("🗓️ Seasonal Intelligence", "Seasonal Intelligence"),
            ("⚠️ Agricultural Risk Analysis", "Agricultural Risk Analysis"),
            ("🧪 What-If Simulator", "What-If Simulator"),
            ("🔍 Explainable AI (XAI)", "Explainable AI"),
            ("📑 AI Decision Reports", "AI Decision Reports"),
            ("🌱 Crop & Soil Advisor", "Crop & Soil Advisor"),
            ("🛡️ Anti-Fraud Detector", "Anti-Fraud Detector"),
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
    elif st.session_state.active_nav == "Seasonal Intelligence":
        render_seasonal_intelligence_view(user, farm)
    elif st.session_state.active_nav == "Agricultural Risk Analysis":
        render_risk_analysis_view(user, farm)
    elif st.session_state.active_nav == "What-If Simulator":
        render_what_if_view(user, farm)
    elif st.session_state.active_nav == "Explainable AI":
        render_explainable_ai_view(user, farm)
    elif st.session_state.active_nav == "AI Decision Reports":
        render_decision_reports_view(user, farm, df_market)
    elif st.session_state.active_nav == "Crop & Soil Advisor":
        render_crop_soil_advisor_view(user, farm)
    elif st.session_state.active_nav == "Anti-Fraud Detector":
        render_anti_fraud_view(user, farm)
    elif st.session_state.active_nav == "Settings":
        render_settings_view(user, farm)

\n'''

updated_content = content[:idx_start] + new_dispatcher + content[idx_end:]

with open(app_path, "w", encoding="utf-8") as f:
    f.write(updated_content)

print("Successfully patched app.py with all 12 views!")
