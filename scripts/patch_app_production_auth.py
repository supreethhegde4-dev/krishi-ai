import os

target_file = "app.py"
with open(target_file, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update tabs on authentication page to include Buyer Registration
old_tabs = """            # View Selector Tabs
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
                    st.rerun()"""

new_tabs = """            # View Selector Tabs (Farmer & Commercial Buyer Portals)
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
                    st.rerun()"""

code_norm = code.replace("\r\n", "\n")
old_tabs_norm = old_tabs.replace("\r\n", "\n")
new_tabs_norm = new_tabs.replace("\r\n", "\n")

if old_tabs_norm in code_norm:
    code_norm = code_norm.replace(old_tabs_norm, new_tabs_norm, 1)

# 2. Clear pre-filled input values in production and hide demo buttons unless KRISHI_ENV=development
old_signin_inputs = """                login_email = st.text_input("Email Address", value="farmer@krishiai.com", placeholder="name@farm.com", key="auth_email")
                login_pwd = st.text_input("Password", value="Password@123", type="password", key="auth_pwd")"""

new_signin_inputs = """                is_dev_env = os.environ.get("KRISHI_ENV", "production").lower() == "development"
                default_email = "farmer@krishiai.com" if is_dev_env else ""
                default_pwd = "Password@123" if is_dev_env else ""
                login_email = st.text_input("Email Address", value=default_email, placeholder="name@farm.com", key="auth_email")
                login_pwd = st.text_input("Password", value=default_pwd, type="password", placeholder="Enter your secret password", key="auth_pwd")"""

old_signin_norm = old_signin_inputs.replace("\r\n", "\n")
new_signin_norm = new_signin_inputs.replace("\r\n", "\n")

if old_signin_norm in code_norm:
    code_norm = code_norm.replace(old_signin_norm, new_signin_norm, 1)

# Wrap demo buttons with is_dev_env check
old_demo_block = """                st.html(\"\"\"
                <div style="text-align:center; margin: 20px 0 12px 0; border-top: 1px solid #E2E8F0; padding-top: 14px;">
                    <span style="background:#F1F5F9; color:#475569; padding:4px 12px; border-radius:12px; font-size:0.75rem; font-weight:800; letter-spacing:0.5px;">
                        ⚡ 1-CLICK INSTANT DEMO ACCESS
                    </span>
                </div>
                \"\"\")

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
                    st.caption("APMC & Agronomic Oversight")"""

new_demo_block = """                if is_dev_env:
                    st.html(\"\"\"
                    <div style="text-align:center; margin: 20px 0 12px 0; border-top: 1px solid #E2E8F0; padding-top: 14px;">
                        <span style="background:#FEF3C7; color:#92400E; padding:4px 12px; border-radius:12px; font-size:0.75rem; font-weight:800; letter-spacing:0.5px;">
                            🧪 DEVELOPMENT SANDBOX TEST ACCOUNTS
                        </span>
                    </div>
                    \"\"\")
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
                        st.caption("Oversight • Sandbox")"""

old_demo_norm = old_demo_block.replace("\r\n", "\n")
new_demo_norm = new_demo_block.replace("\r\n", "\n")

if old_demo_norm in code_norm:
    code_norm = code_norm.replace(old_demo_norm, new_demo_norm, 1)

# 3. Add buyer_signup view handler
buyer_signup_view = """
            elif st.session_state.auth_view == "buyer_signup":
                st.html(\"\"\"
                <div style="margin-bottom: 14px;">
                    <h3 style="color:#0D5C3A; font-size:1.35rem; font-weight:800; margin:0 0 2px 0;">Commercial Buyer & Industry Registration</h3>
                    <div style="color:#64748B; font-size:0.88rem;">Register your corporate processing plant, retail chain, or wholesale aggregator entity</div>
                </div>
                \"\"\")

                b_company = st.text_input("Company / Business Name *", placeholder="e.g. Kaveri Agro Processing Pvt Ltd")
                b_type = st.selectbox("Business Model *", [
                    "Food Processing & FMCG", "Wholesale & Supermarket Chain",
                    "Cold Chain & Horticultural Aggregator", "Flour & Pulse Milling Hub",
                    "Export Trading House", "Dairy & Organic Products"
                ])
                b_gstin = st.text_input("GSTIN / Business Registration Number *", placeholder="e.g. 29AABCU9603R1ZM", help="Required for official APMC trade auditing and settlement protection")
                b_apmc_lic = st.text_input("APMC Trader License Number (Optional)", placeholder="e.g. APMC-KAR-8821")
                b_name = st.text_input("Authorized Contact Person *", placeholder="e.g. Suresh Varma")
                b_phone = st.text_input("Contact Mobile Phone *", placeholder="+91 98450 12345")
                b_email = st.text_input("Corporate Email Address *", placeholder="procure@kaveriagro.com")
                b_addr = st.text_input("Processing Facility / Warehouse Address *", placeholder="Plot 14, KIADB Industrial Area, Bidadi")
                b_dist = st.text_input("Facility District *", value="Ramanagara")
                b_state = st.text_input("State *", value="Karnataka")
                b_pwd = st.text_input("Create Security Password *", type="password", help="Minimum 8 characters with at least one uppercase letter and one number")
                b_pwd_conf = st.text_input("Confirm Security Password *", type="password")
                b_agree = st.checkbox("I agree to Krishi AI Commercial B2B Marketplace Terms, APMC Settlement Rules, and DPDP Act Privacy Notice")

                if st.button("Submit Buyer Registration Application →", type="primary", use_container_width=True):
                    if not b_company or not b_name or not b_email or not b_pwd or not b_gstin:
                        st.error("Please fill in all required fields marked with *.")
                    elif b_pwd != b_pwd_conf:
                        st.error("Passwords do not match.")
                    elif not b_agree:
                        st.error("You must accept the commercial terms of service to register.")
                    else:
                        with st.spinner("Processing buyer registration..."):
                            from modules.buyer_connect_db import register_buyer_profile
                            success, msg = register_user(
                                full_name=b_name,
                                email=b_email,
                                password=b_pwd,
                                phone=b_phone,
                                role="buyer"
                            )
                            if success:
                                # Authenticate to get user ID
                                _, _, _, u_info = authenticate_user(b_email, b_pwd)
                                if u_info:
                                    register_buyer_profile(
                                        user_id=u_info["id"],
                                        company_name=b_company,
                                        business_type=b_type,
                                        contact_person=b_name,
                                        phone=b_phone,
                                        email=b_email,
                                        facility_address=b_addr,
                                        district=b_dist,
                                        state=b_state,
                                        latitude=12.7981,
                                        longitude=77.4005,
                                        gstin=b_gstin,
                                        apmc_license=b_apmc_lic
                                    )
                                st.success("Buyer account created successfully! Please sign in with your corporate credentials.")
                                st.session_state.auth_view = "signin"
                                st.rerun()
                            else:
                                st.error(msg)
"""

if "st.session_state.auth_view == \"buyer_signup\"" not in code_norm:
    insert_pos = code_norm.find("elif st.session_state.auth_view == \"signup\":")
    if insert_pos != -1:
        code_norm = code_norm[:insert_pos] + buyer_signup_view + "\n            " + code_norm[insert_pos:]

with open(target_file, "w", encoding="utf-8") as f:
    f.write(code_norm)

print("SUCCESS: Patched app.py for production authentication")
