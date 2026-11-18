"""
High-Contrast UI View for Buyer & Industry Connect in Krishi AI.
Provides:
1. Smart Buyer Matching & Nearby Discovery (Distance, Freight & Net Profit Ranking)
2. Industry Purchasing Catalog (Specifications, Moisture, Delivery Deadlines)
3. Farmer Quotation Submission & Lifecycle Tracker (Pending, Accepted, Rejected)
4. Industry Buyer Portal (Post Requirements, Review & Accept/Reject Quotations)
5. Verified Agro-Buyer Directory & Contract Slips
"""
import datetime
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from modules.buyer_connect_db import (
    get_all_buyers, get_active_requirements, get_requirement_by_id,
    create_buyer_requirement, submit_farmer_quotation,
    get_quotations_by_farmer, get_quotations_for_buyer,
    update_quotation_status, update_requirement_status, get_buyer_by_id
)
from modules.smart_buyer_matcher import match_buyers_for_farmer
from modules.transport_engine import DEFAULT_VEHICLE_CONFIGS


def render_buyer_connect_view(user, farm, df_market=None):
    st.markdown("#### 🤝 Buyer & Industry Connect")
    st.caption("Direct Industrial Procurement, Smart Demand Matching & Direct Farmer Quotation System.")

    # 1. ORIGIN & LOCATION RESOLUTION
    farmer_lat = float(farm.get("latitude", 12.7209))
    farmer_lon = float(farm.get("longitude", 77.2799))
    farmer_name = user.get("full_name", "Farmer Producer")
    farmer_phone = user.get("phone", "+91 98450 12345")
    farmer_district = farm.get("district", "Ramanagara")
    farmer_state = farm.get("state", "Karnataka")

    # Location override accordion / expander
    with st.expander("📍 Dispatch Origin & Location Configuration", expanded=False):
        c_l1, c_l2, c_l3 = st.columns([1.5, 1, 1])
        with c_l1:
            st.info(f"**Current Profile Origin:** {farm.get('farm_name', 'Farm Enterprise')} — {farmer_district}, {farmer_state} ({farmer_lat:.4f}°N, {farmer_lon:.4f}°E)")
        with c_l2:
            custom_lat = st.number_input("Override Latitude", value=farmer_lat, format="%.4f", key="bc_custom_lat")
        with c_l3:
            custom_lon = st.number_input("Override Longitude", value=farmer_lon, format="%.4f", key="bc_custom_lon")
        if custom_lat != farmer_lat or custom_lon != farmer_lon:
            farmer_lat, farmer_lon = custom_lat, custom_lon
            st.success(f"Using custom dispatch coordinates: {farmer_lat:.4f}°N, {farmer_lon:.4f}°E")

    # 2. EXECUTIVE KPI ROW
    buyers_list = get_all_buyers()
    active_reqs = get_active_requirements()
    farmer_quots = get_quotations_by_farmer(user["id"])
    accepted_cnt = sum(1 for q in farmer_quots if q["status"] == "ACCEPTED")

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric(label="Active Purchasing Requirements", value=f"{len(active_reqs)} Open Lots", delta="Procurement Live")
    with k2:
        st.metric(label="Verified Industry Buyers", value=f"{len(buyers_list)} Enterprises", delta="100% KYC Verified")
    with k3:
        max_price_offer = max((r["offered_price_per_quintal"] for r in active_reqs), default=0.0)
        st.metric(label="Top Industrial Price", value=f"₹{max_price_offer:,.0f} / Qtl", delta="Premium Lots")
    with k4:
        st.metric(label="My Quotation Pipeline", value=f"{len(farmer_quots)} Submitted", delta=f"{accepted_cnt} Accepted Contract" if accepted_cnt else "Active Bidding")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 3. TAB NAVIGATION
    tab_match, tab_catalog, tab_my_quotes, tab_buyer_portal, tab_directory = st.tabs([
        "🎯 Smart Deal Matcher",
        "🏢 Active Industry Requirements",
        "📝 My Quotations Tracker",
        "🏭 Industry Buyer Workspace",
        "📜 Verified Buyers Directory"
    ])

    # ==========================================================================
    # TAB 1: SMART DEAL MATCHER & NEARBY DISCOVERY
    # ==========================================================================
    with tab_match:
        st.markdown("##### 🔍 Multi-Factor Industrial Buyer Matcher")
        st.caption("Ranks nearby agro-processors based on road distance, freight deduction, quality specifications, and net farmer profit advantage over local APMC mandi.")

        col_m1, col_m2, col_m3, col_m4 = st.columns([1.2, 1.2, 1.2, 1.2])

        PRIMARY_CROPS = ["Tomato", "Onion", "Potato", "Wheat", "Maize", "Banana", "Cabbage", "All Crops"]
        farm_crop = farm.get("primary_crops", "Tomato").split(",")[0].strip()
        crop_idx = PRIMARY_CROPS.index(farm_crop) if farm_crop in PRIMARY_CROPS else 0

        with col_m1:
            sel_crop = st.selectbox("Harvest Crop", PRIMARY_CROPS, index=crop_idx, key="matcher_crop")
        with col_m2:
            sel_qty = st.number_input("Available Lot (Quintals)", min_value=5.0, max_value=2000.0, value=30.0, step=5.0, key="matcher_qty")
        with col_m3:
            sel_grade = st.selectbox("Offered Quality Grade", ["Grade A (Premium)", "Grade B (Standard)", "Grade C (Commercial)", "Certified Organic"], index=0, key="matcher_grade")
        with col_m4:
            sel_radius = st.selectbox("Max Road Distance", ["50 km", "100 km", "200 km", "350 km", "All Distances"], index=2, key="matcher_radius")

        radius_km = None if sel_radius == "All Distances" else float(sel_radius.split()[0])

        # Benchmark mandi price estimation
        mandi_benchmark = 2100.0
        if sel_crop == "Potato":
            mandi_benchmark = 1750.0
        elif sel_crop == "Onion":
            mandi_benchmark = 2250.0
        elif sel_crop == "Wheat":
            mandi_benchmark = 2450.0
        elif sel_crop == "Maize":
            mandi_benchmark = 1950.0
        elif sel_crop == "Banana":
            mandi_benchmark = 1600.0

        with st.spinner("Calculating road routing, freight economics, and compatibility matching..."):
            matched_deals = match_buyers_for_farmer(
                farmer_lat=farmer_lat,
                farmer_lon=farmer_lon,
                crop=sel_crop,
                quantity_quintals=sel_qty,
                farmer_grade=sel_grade,
                max_distance_km=radius_km,
                benchmark_mandi_price_qtl=mandi_benchmark
            )

        if not matched_deals:
            st.warning(f"No active industrial requirements found matching {sel_crop} within {sel_radius}. Try expanding the distance radius or checking other crops.")
        else:
            top_deal = matched_deals[0]

            # Top Recommended Deal Banner
            st.html(f"""
            <div style="background:linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%); border:1.8px solid #86EFAC; border-radius:12px; padding:18px 22px; margin: 12px 0 20px 0;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                    <div>
                        <div style="display:inline-flex; align-items:center; gap:6px; background:#15803D; color:#FFFFFF; padding:3px 10px; border-radius:12px; font-size:0.75rem; font-weight:800; letter-spacing:0.5px;">
                            {top_deal['match_badge']}
                        </div>
                        <div style="font-size:1.4rem; font-weight:800; color:#0D5C3A; margin:6px 0 2px 0;">{top_deal['company_name']}</div>
                        <div style="font-size:0.88rem; color:#475569;">
                            📍 {top_deal['facility_address']} ({top_deal['distance_km']} km • ~{top_deal['duration_hours']}h transit) • ⭐ {top_deal['buyer_rating']} Rating
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:0.82rem; color:#64748B; font-weight:700;">ESTIMATED NET REVENUE</div>
                        <div style="font-size:1.75rem; font-weight:800; color:#0D5C3A;">₹{top_deal['net_revenue']:,.2f}</div>
                        <div style="font-size:0.82rem; color:#15803D; font-weight:800; background:#FFFFFF; padding:2px 8px; border-radius:6px; border:1px solid #86EFAC; display:inline-block;">
                            ₹{top_deal['net_profit_delta']:+,.2f} ({top_deal['roi_gain_pct']:+.1f}% vs Local Mandi)
                        </div>
                    </div>
                </div>
            </div>
            """)

            st.markdown(f"**Found {len(matched_deals)} Purchasing Deals Ranked by Match Suitability & Farmer Net Margin:**")

            for idx, deal in enumerate(matched_deals):
                with st.container(border=True):
                    d_col1, d_col2 = st.columns([2.2, 1.2])

                    with d_col1:
                        st.html(f"""
                        <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                            <span style="background:{deal['badge_color']}; color:#FFFFFF; font-size:0.75rem; font-weight:800; padding:3px 8px; border-radius:12px;">
                                {deal['match_badge']}
                            </span>
                            <span style="font-size:1.15rem; font-weight:800; color:#0F172A;">{deal['company_name']}</span>
                            <span style="font-size:0.78rem; color:#15803D; background:#DCFCE7; padding:2px 6px; border-radius:4px; font-weight:700;">✓ Verified Buyer</span>
                        </div>
                        <div style="font-size:0.85rem; color:#475569; margin-bottom:8px;">
                            <b>Procurement Requirement:</b> {deal['required_quantity_quintals']:.0f} Quintals of {deal['crop']} ({deal['min_quality_grade']})<br>
                            <b>Delivery Facility:</b> {deal['delivery_location']} • <b>Distance:</b> {deal['distance_km']} km (~{deal['duration_hours']} hrs drive)
                        </div>
                        <div style="font-size:0.82rem; color:#334155; background:#F8FAF8; padding:8px 12px; border-radius:6px; border:1px solid #E2E8F0; margin-bottom:8px;">
                            <b>Specifications:</b> {deal['additional_specs'] or 'Standard agricultural procurement terms'}<br>
                            <b>Payment Terms:</b> {deal['payment_terms']} • <b>Deadline:</b> {deal['required_by_date']}
                        </div>
                        """)

                    with d_col2:
                        st.html(f"""
                        <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:10px 14px; text-align:right;">
                            <div style="font-size:0.78rem; color:#64748B; font-weight:700;">OFFERED PRICE</div>
                            <div style="font-size:1.35rem; font-weight:800; color:#0D5C3A;">₹{deal['offered_price_per_quintal']:,.0f} <span style="font-size:0.8rem; color:#64748B;">/ Qtl</span></div>
                            <div style="font-size:0.8rem; color:#475569;">₹{deal['offered_price_per_kg']:.2f} / kg</div>
                            <hr style="margin:6px 0; border:none; border-top:1px solid #E2E8F0;">
                            <div style="display:flex; justify-content:space-between; font-size:0.78rem; color:#64748B;">
                                <span>Gross:</span> <span>₹{deal['gross_revenue']:,.0f}</span>
                            </div>
                            <div style="display:flex; justify-content:space-between; font-size:0.78rem; color:#64748B;">
                                <span>Est. Freight:</span> <span style="color:#DC2626;">-₹{deal['total_freight_cost']:,.0f}</span>
                            </div>
                            <div style="display:flex; justify-content:space-between; font-size:0.85rem; font-weight:800; color:#0F172A; margin-top:2px;">
                                <span>Net Farmer:</span> <span style="color:#0D5C3A;">₹{deal['net_revenue']:,.0f}</span>
                            </div>
                            <div style="font-size:0.75rem; font-weight:700; color:#15803D; margin-top:4px;">
                                Suitability Score: {deal['suitability_score']}/100
                            </div>
                        </div>
                        """)

                    # Submission Expander
                    with st.expander(f"📝 Submit Direct Quotation to {deal['company_name']}", expanded=False):
                        q_col1, q_col2 = st.columns(2)
                        with q_col1:
                            q_qty = st.number_input("Supply Quantity (Quintals)", min_value=1.0, max_value=deal['required_quantity_quintals']*2, value=float(sel_qty), key=f"q_qty_{deal['requirement_id']}")
                            q_price = st.number_input("Quoted Price (₹ / Quintal)", min_value=500.0, max_value=10000.0, value=float(deal['offered_price_per_quintal']), step=50.0, key=f"q_price_{deal['requirement_id']}")
                            q_grade = st.selectbox("Offered Quality Grade", ["Grade A (Premium)", "Grade B (Standard)", "Grade C (Commercial)", "Certified Organic"], index=0, key=f"q_grade_{deal['requirement_id']}")
                        with q_col2:
                            q_deliv_date = st.date_input("Expected Delivery Date", value=datetime.date.today() + datetime.timedelta(days=3), key=f"q_date_{deal['requirement_id']}")
                            q_notes = st.text_area("Farmer Dispatch Notes / Conditions", value="Morning harvest, carefully graded and packaged in clean crates. Ready for weighbridge quality inspection.", key=f"q_notes_{deal['requirement_id']}")

                        q_gross = q_qty * q_price
                        st.html(f"<div style='font-size:0.85rem; color:#0D5C3A; font-weight:700; margin:6px 0 10px 0;'>Estimated Quotation Gross Value: ₹{q_gross:,.2f} ({q_qty:.0f} Quintals @ ₹{q_price:,.0f}/Qtl)</div>")

                        if st.button(f"🚀 Confirm & Submit Formal Quotation #{deal['requirement_id']}", key=f"btn_sub_{deal['requirement_id']}", type="primary"):
                            sub_ok, sub_msg, new_qid = submit_farmer_quotation(
                                requirement_id=deal["requirement_id"],
                                farmer_id=user["id"],
                                farmer_name=farmer_name,
                                farmer_phone=farmer_phone,
                                crop=deal["crop"],
                                offered_quantity_quintals=q_qty,
                                quoted_price_per_quintal=q_price,
                                offered_grade=q_grade,
                                dispatch_location=farm.get("village", "Farm Holding"),
                                dispatch_district=farmer_district,
                                dispatch_state=farmer_state,
                                dispatch_lat=farmer_lat,
                                dispatch_lon=farmer_lon,
                                expected_delivery_date=q_deliv_date.strftime("%Y-%m-%d"),
                                farmer_notes=q_notes
                            )
                            if sub_ok:
                                st.success(sub_msg)
                                st.rerun()
                            else:
                                st.error(sub_msg)

    # ==========================================================================
    # TAB 2: ACTIVE INDUSTRY REQUIREMENTS DIRECTORY
    # ==========================================================================
    with tab_catalog:
        st.markdown("##### 📦 All Active Industrial Purchasing Requirements")
        st.caption("Live procurement notices published by food processing companies, retail aggregators, and commercial flour/feed mills.")

        r_f1, r_f2, r_f3 = st.columns(3)
        with r_f1:
            cat_crop = st.selectbox("Filter by Crop", ["All Crops", "Tomato", "Potato", "Onion", "Wheat", "Maize", "Banana", "Cabbage"], key="cat_crop")
        with r_f2:
            cat_grade = st.selectbox("Filter by Grade", ["All Grades", "Grade A (Premium)", "Grade B (Standard)", "Certified Organic"], key="cat_grade")
        with r_f3:
            cat_min_p = st.number_input("Minimum Price (₹/Qtl)", min_value=0.0, value=0.0, step=200.0, key="cat_min_p")

        cat_reqs = get_active_requirements(
            crop=None if cat_crop == "All Crops" else cat_crop,
            grade=None if cat_grade == "All Grades" else cat_grade,
            min_price=cat_min_p
        )

        st.info(f"Displaying **{len(cat_reqs)}** open industrial procurement requirements.")

        for r in cat_reqs:
            with st.container(border=True):
                r_c1, r_c2, r_c3 = st.columns([2, 1.2, 1])

                with r_c1:
                    st.html(f"""
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span style="font-size:1.1rem; font-weight:800; color:#0D5C3A;">{r['company_name']}</span>
                        <span style="font-size:0.75rem; font-weight:700; color:#FFFFFF; background:{'#DC2626' if r['urgency_level'] == 'Urgent' else '#0D5C3A'}; padding:2px 6px; border-radius:4px;">
                            {r['urgency_level'].upper()}
                        </span>
                        <span style="font-size:0.75rem; color:#15803D; font-weight:700; background:#DCFCE7; padding:2px 6px; border-radius:4px;">✓ Verified</span>
                    </div>
                    <div style="font-size:0.85rem; color:#475569; margin:4px 0;">
                        <b>Crop:</b> <span style="color:#0F172A; font-weight:700;">{r['crop']}</span> • <b>Volume Required:</b> {r['quantity_quintals']:.0f} Quintals ({r['min_quality_grade']})
                    </div>
                    <div style="font-size:0.82rem; color:#334155;">
                        📍 <b>Delivery At:</b> {r['delivery_location']} ({r['delivery_district']}, {r['delivery_state']})<br>
                        📋 <b>Quality Specs:</b> {r['additional_specs'] or 'Standard gate quality test'}
                    </div>
                    """)

                with r_c2:
                    st.html(f"""
                    <div style="background:#F8FAF8; border:1px solid #E2E8F0; border-radius:8px; padding:10px; text-align:center;">
                        <div style="font-size:0.75rem; color:#64748B; font-weight:700;">OFFERED PRICE</div>
                        <div style="font-size:1.3rem; font-weight:800; color:#0D5C3A;">₹{r['offered_price_per_quintal']:,.0f}</div>
                        <div style="font-size:0.78rem; color:#64748B;">₹{r['offered_price_per_quintal']/100.0:.2f} / kg</div>
                        <div style="font-size:0.75rem; color:#B45309; font-weight:700; margin-top:4px;">Required by: {r['required_by_date']}</div>
                    </div>
                    """)

                with r_c3:
                    st.html(f"""
                    <div style="font-size:0.8rem; color:#475569; margin-bottom:6px;">
                        <b>Contact:</b> {r['contact_person']}<br>
                        📞 {r.get('buyer_phone', 'Confidential')}<br>
                        ✉️ {r.get('buyer_email', '')}
                    </div>
                    """)
                    if st.button("Quote This Lot", key=f"btn_direct_quote_{r['id']}", use_container_width=True):
                        st.session_state[f"show_quote_form_{r['id']}"] = not st.session_state.get(f"show_quote_form_{r['id']}", False)

                if st.session_state.get(f"show_quote_form_{r['id']}", False):
                    with st.container(border=True):
                        st.markdown(f"**Submit Quotation for Requirement #{r['id']} ({r['crop']})**")
                        cq1, cq2 = st.columns(2)
                        with cq1:
                            cq_qty = st.number_input("Supply Quantity (Quintals)", min_value=1.0, value=25.0, key=f"cat_q_qty_{r['id']}")
                            cq_price = st.number_input("Quoted Price (₹/Quintal)", min_value=100.0, value=float(r['offered_price_per_quintal']), key=f"cat_q_price_{r['id']}")
                        with cq2:
                            cq_grade = st.selectbox("Offered Grade", ["Grade A (Premium)", "Grade B (Standard)", "Grade C (Commercial)", "Certified Organic"], key=f"cat_q_grade_{r['id']}")
                            cq_date = st.date_input("Delivery Date", value=datetime.date.today() + datetime.timedelta(days=4), key=f"cat_q_date_{r['id']}")

                        cq_notes = st.text_input("Special Conditions / Loading Terms", value="Delivery directly to buyer factory bay.", key=f"cat_q_notes_{r['id']}")

                        if st.button(f"Submit Quotation to {r['company_name']}", key=f"cat_btn_sub_{r['id']}", type="primary"):
                            sub_ok, sub_msg, new_qid = submit_farmer_quotation(
                                requirement_id=r["id"],
                                farmer_id=user["id"],
                                farmer_name=farmer_name,
                                farmer_phone=farmer_phone,
                                crop=r["crop"],
                                offered_quantity_quintals=cq_qty,
                                quoted_price_per_quintal=cq_price,
                                offered_grade=cq_grade,
                                dispatch_location=farm.get("village", "Farm Holding"),
                                dispatch_district=farmer_district,
                                dispatch_state=farmer_state,
                                dispatch_lat=farmer_lat,
                                dispatch_lon=farmer_lon,
                                expected_delivery_date=cq_date.strftime("%Y-%m-%d"),
                                farmer_notes=cq_notes
                            )
                            if sub_ok:
                                st.success(sub_msg)
                                st.session_state[f"show_quote_form_{r['id']}"] = False
                                st.rerun()
                            else:
                                st.error(sub_msg)

    # ==========================================================================
    # TAB 3: MY SUBMITTED QUOTATIONS (FARMER TRACKER)
    # ==========================================================================
    with tab_my_quotes:
        st.markdown("##### 📝 My Submitted Quotations & Contract Pipeline")
        st.caption("Track the lifecycle of your submitted quotations. Buyers can accept, review, or propose counter-prices.")

        user_quotes = get_quotations_by_farmer(user["id"])

        if not user_quotes:
            st.info("You have not submitted any quotations yet. Use the **Smart Deal Matcher** or **Active Requirements** tabs to bid on procurement lots.")
        else:
            q_filter = st.radio("Filter Status", ["All", "ACCEPTED", "UNDER_REVIEW", "PENDING", "REJECTED"], horizontal=True, key="my_q_filter")

            filtered_quotes = [q for q in user_quotes if q_filter == "All" or q["status"] == q_filter]

            st.write(f"Showing **{len(filtered_quotes)}** quotations.")

            for q in filtered_quotes:
                with st.container(border=True):
                    # Status color coding
                    if q["status"] == "ACCEPTED":
                        st_color = "#15803D"
                        st_bg = "#DCFCE7"
                        st_badge = "🟢 CONTRACT ACCEPTED"
                    elif q["status"] == "UNDER_REVIEW":
                        st_color = "#D97706"
                        st_bg = "#FEF3C7"
                        st_badge = "🟡 UNDER REVIEW"
                    elif q["status"] == "REJECTED":
                        st_color = "#DC2626"
                        st_bg = "#FEE2E2"
                        st_badge = "🔴 QUOTATION REJECTED"
                    elif q["status"] == "COUNTER_OFFER":
                        st_color = "#2563EB"
                        st_bg = "#DBEAFE"
                        st_badge = "🔵 BUYER COUNTER-OFFER"
                    else:
                        st_color = "#64748B"
                        st_bg = "#F1F5F9"
                        st_badge = "⚪ PENDING BUYER REVIEW"

                    q_val = q["offered_quantity_quintals"] * q["quoted_price_per_quintal"]

                    qc1, qc2 = st.columns([2.2, 1.2])
                    with qc1:
                        st.html(f"""
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span style="font-size:1.15rem; font-weight:800; color:#0F172A;">Quotation #{q['id']} — {q['crop']}</span>
                            <span style="background:{st_bg}; color:{st_color}; padding:4px 10px; border-radius:12px; font-size:0.78rem; font-weight:800;">
                                {st_badge}
                            </span>
                        </div>
                        <div style="font-size:0.85rem; color:#475569; margin-bottom:6px;">
                            <b>Buyer Company:</b> {q['buyer_company']} • <b>Contact:</b> {q['buyer_contact']} ({q.get('buyer_phone', '')})<br>
                            <b>Submitted Lot:</b> {q['offered_quantity_quintals']:.0f} Quintals of {q['offered_grade']} @ <b style="color:#0D5C3A;">₹{q['quoted_price_per_quintal']:,.0f}/Qtl</b> (Total Value: ₹{q_val:,.2f})<br>
                            <b>Expected Dispatch Date:</b> {q['expected_delivery_date']} • <b>Destination:</b> {q['buyer_facility']}
                        </div>
                        <div style="font-size:0.82rem; color:#334155; background:#F8FAF8; padding:8px 10px; border-radius:6px; border:1px solid #E2E8F0;">
                            <b>Your Dispatch Note:</b> {q['farmer_notes'] or 'None provided'}
                        </div>
                        """)

                        if q.get("buyer_feedback"):
                            st.html(f"""
                            <div style="font-size:0.82rem; color:{st_color}; background:{st_bg}; padding:8px 10px; border-radius:6px; margin-top:6px; border-left:3px solid {st_color};">
                                <b>Buyer Response:</b> {q['buyer_feedback']}
                            </div>
                            """)

                    with qc2:
                        st.html(f"""
                        <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:10px; text-align:center;">
                            <div style="font-size:0.75rem; color:#64748B; font-weight:700;">PAYMENT TERMS</div>
                            <div style="font-size:0.82rem; font-weight:700; color:#0D5C3A; margin:3px 0 8px 0;">{q.get('payment_terms', 'Standard')}</div>
                            <div style="font-size:0.75rem; color:#64748B;">Buyer Required Price: ₹{q['buyer_offered_price']:,.0f}/Qtl</div>
                            <div style="font-size:0.75rem; color:#64748B;">Submitted On: {q['created_at'][:10]}</div>
                        </div>
                        """)

                        if q["status"] == "ACCEPTED":
                            with st.expander("📄 View Deal Slip", expanded=False):
                                st.html(f"""
                                <div style="font-size:0.8rem; line-height:1.4; color:#0F172A; background:#F8FAF8; padding:8px; border-radius:6px;">
                                    <b>CONTRACT CONFIRMATION</b><br>
                                    Buyer: {q['buyer_company']}<br>
                                    Produce: {q['crop']} ({q['offered_quantity_quintals']:.0f} Qtl)<br>
                                    Agreed Rate: ₹{q['quoted_price_per_quintal']:,.0f}/Qtl<br>
                                    Total Payable: ₹{q_val:,.2f}<br>
                                    Delivery: {q['buyer_facility']}<br>
                                    Date: {q['expected_delivery_date']}
                                </div>
                                """)

    # ==========================================================================
    # TAB 4: INDUSTRY BUYER WORKSPACE (POST & REVIEW BIDS)
    # ==========================================================================
    with tab_buyer_portal:
        st.markdown("##### 🏭 Industry Procurement Management Portal")
        st.caption("Procurement managers can publish corporate crop intake requirements and evaluate incoming farmer bids.")

        col_b_act1, col_b_act2 = st.columns([1.5, 1])
        with col_b_act1:
            st.info("💡 **Procurement Officer Mode:** You can post new raw material requirements and review/accept farmer quotations.")
        with col_b_act2:
            buyer_selector = st.selectbox("Operating as Enterprise", [b["company_name"] for b in buyers_list], index=0, key="portal_buyer_sel")

        active_buyer = next((b for b in buyers_list if b["company_name"] == buyer_selector), buyers_list[0])

        with st.expander(f"➕ Publish New Crop Requirement for {active_buyer['company_name']}", expanded=False):
            with st.form("form_post_requirement"):
                p_c1, p_c2, p_c3 = st.columns(3)
                with p_c1:
                    post_crop = st.selectbox("Crop Required", ["Tomato", "Potato", "Onion", "Wheat", "Maize", "Banana", "Cabbage", "Rice", "Soybean"], key="p_crop")
                    post_qty = st.number_input("Required Batch (Quintals)", min_value=10.0, value=200.0, step=10.0, key="p_qty")
                    post_grade = st.selectbox("Minimum Quality Grade", ["Grade A (Premium)", "Grade B (Standard)", "Grade C (Commercial)", "Certified Organic"], key="p_grade")
                with p_c2:
                    post_price = st.number_input("Offered Price (₹ / Quintal)", min_value=500.0, value=2500.0, step=50.0, key="p_price")
                    post_urgency = st.selectbox("Urgency", ["Standard", "Urgent", "Contract Season"], key="p_urg")
                    post_date = st.date_input("Delivery Deadline", value=datetime.date.today() + datetime.timedelta(days=10), key="p_date")
                with p_c3:
                    post_loc = st.text_input("Delivery Facility Address", value=active_buyer["facility_address"], key="p_loc")
                    post_specs = st.text_area("Quality & Testing Specifications", value="Moisture < 12%, sorted uniform size, no pest infestation. Weighbridge gate intake with instant lab test.", key="p_specs")

                btn_publish = st.form_submit_button("Publish Requirement to Network", type="primary")
                if btn_publish:
                    pub_ok, pub_msg, new_rid = create_buyer_requirement(
                        buyer_id=active_buyer["id"],
                        crop=post_crop,
                        quantity_quintals=post_qty,
                        min_quality_grade=post_grade,
                        offered_price_per_quintal=post_price,
                        delivery_location=post_loc,
                        delivery_district=active_buyer["district"],
                        delivery_state=active_buyer["state"],
                        delivery_lat=active_buyer["latitude"],
                        delivery_lon=active_buyer["longitude"],
                        required_by_date=post_date.strftime("%Y-%m-%d"),
                        additional_specs=post_specs,
                        urgency_level=post_urgency
                    )
                    if pub_ok:
                        st.success(pub_msg)
                        st.rerun()
                    else:
                        st.error(pub_msg)

        # Review Received Farmer Quotations for this buyer
        buyer_received_quots = get_quotations_for_buyer(active_buyer["id"])

        st.markdown(f"**Incoming Farmer Quotations for {active_buyer['company_name']} ({len(buyer_received_quots)} Total):**")

        if not buyer_received_quots:
            st.info(f"No farmer quotations have been submitted to {active_buyer['company_name']} yet. As registered farmers submit quotes against your posted requirements, they will appear here.")
        else:
            for bq in buyer_received_quots:
                with st.container(border=True):
                    bq_c1, bq_c2 = st.columns([2.2, 1.2])

                    with bq_c1:
                        st.html(f"""
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:1.1rem; font-weight:800; color:#0F172A;">Quotation #{bq['id']} — {bq['farmer_name']}</span>
                            <span style="font-size:0.78rem; font-weight:700; color:#475569; background:#E2E8F0; padding:2px 8px; border-radius:12px;">{bq['status']}</span>
                        </div>
                        <div style="font-size:0.85rem; color:#475569; margin:4px 0;">
                            <b>Commodity:</b> {bq['crop']} ({bq['offered_grade']}) • <b>Volume:</b> {bq['offered_quantity_quintals']:.0f} Quintals<br>
                            <b>Quoted Rate:</b> <span style="font-size:1.05rem; font-weight:800; color:#0D5C3A;">₹{bq['quoted_price_per_quintal']:,.0f}/Qtl</span> (Requirement Budget: ₹{bq['req_price']:,.0f}/Qtl)<br>
                            <b>Farmer Origin:</b> {bq['dispatch_location']} ({bq['dispatch_district']}) • 📞 {bq['farmer_phone']}<br>
                            <b>Expected Delivery:</b> {bq['expected_delivery_date']}
                        </div>
                        <div style="font-size:0.8rem; color:#334155; background:#F8FAF8; padding:6px 10px; border-radius:6px; border:1px solid #E2E8F0;">
                            <b>Farmer Note:</b> {bq['farmer_notes'] or 'None'}
                        </div>
                        """)

                    with bq_c2:
                        total_lot_val = bq['offered_quantity_quintals'] * bq['quoted_price_per_quintal']
                        st.html(f"""
                        <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:10px; text-align:center; margin-bottom:8px;">
                            <div style="font-size:0.75rem; color:#64748B; font-weight:700;">TOTAL LOT VALUE</div>
                            <div style="font-size:1.25rem; font-weight:800; color:#0D5C3A;">₹{total_lot_val:,.2f}</div>
                        </div>
                        """)

                        # Review Action Buttons
                        b_act1, b_act2 = st.columns(2)
                        with b_act1:
                            if st.button("✓ Accept Bid", key=f"btn_accept_{bq['id']}", type="primary", use_container_width=True):
                                ok_up, msg_up = update_quotation_status(
                                    quotation_id=bq["id"],
                                    new_status="ACCEPTED",
                                    feedback="Quotation accepted. Please deliver produce to factory gate with weight slip."
                                )
                                if ok_up:
                                    st.success(msg_up)
                                    st.rerun()
                        with b_act2:
                            if st.button("✕ Reject Bid", key=f"btn_reject_{bq['id']}", use_container_width=True):
                                ok_up, msg_up = update_quotation_status(
                                    quotation_id=bq["id"],
                                    new_status="REJECTED",
                                    feedback="Quotation rejected: Lot does not meet current processing window."
                                )
                                if ok_up:
                                    st.warning(msg_up)
                                    st.rerun()

    # ==========================================================================
    # TAB 5: VERIFIED BUYERS DIRECTORY
    # ==========================================================================
    with tab_directory:
        st.markdown("##### 📜 Registered & KYC-Verified Agricultural Buyers")
        st.caption("Pre-screened corporate processors, export houses, and supermarket procurement chains operating on Krishi AI.")

        for b in buyers_list:
            with st.container(border=True):
                bd1, bd2 = st.columns([2.5, 1.2])
                with bd1:
                    st.html(f"""
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span style="font-size:1.15rem; font-weight:800; color:#0D5C3A;">{b['company_name']}</span>
                        <span style="font-size:0.78rem; font-weight:700; color:#15803D; background:#DCFCE7; padding:2px 8px; border-radius:12px;">✓ 100% KYC Verified</span>
                        <span style="font-size:0.78rem; color:#B45309; font-weight:700;">★ {b['rating']} ({b['total_deals_completed']} Deals Completed)</span>
                    </div>
                    <div style="font-size:0.85rem; color:#475569; margin:4px 0 6px 0;">
                        <b>Industry Category:</b> {b['business_type']} • <b>Location:</b> {b['district']}, {b['state']}
                    </div>
                    <div style="font-size:0.82rem; color:#334155;">
                        📍 <b>Facility Address:</b> {b['facility_address']}<br>
                        💳 <b>Payment Terms:</b> {b['payment_terms']}
                    </div>
                    """)

                with bd2:
                    st.html(f"""
                    <div style="background:#F8FAF8; border:1px solid #E2E8F0; border-radius:8px; padding:10px; font-size:0.82rem;">
                        <b>Key Procurement Officer:</b><br>
                        {b['contact_person']}<br>
                        📞 {b['phone']}<br>
                        ✉️ {b['email']}
                    </div>
                    """)
