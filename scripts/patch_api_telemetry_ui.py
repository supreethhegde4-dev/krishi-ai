"""
Patches modules/ui_views.py to render External API Telemetry & Persistence Health in Settings.
"""
import os

views_path = os.path.join(os.path.dirname(__file__), "..", "modules", "ui_views.py")

with open(views_path, "r", encoding="utf-8") as f:
    content = f.read()

target = """                if st.button("💾 Trigger Atomic Online Backup Snapshot", use_container_width=True):
                    b_ok, b_msg, b_file = backup_database()
                    if b_ok:
                        st.success(b_msg)
                    else:
                        st.error(b_msg)"""

replacement = """                if st.button("💾 Trigger Atomic Online Backup Snapshot", use_container_width=True):
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
                st.html(f\"\"\"
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
                \"\"\")"""

content = content.replace(target.replace("\r\n", "\n"), replacement.replace("\r\n", "\n"))
content = content.replace(target.replace("\n", "\r\n"), replacement.replace("\n", "\r\n"))

with open(views_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully added API telemetry card to Profile & Settings view.")
