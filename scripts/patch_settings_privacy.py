import os

target_file = "modules/ui_views.py"
with open(target_file, "r", encoding="utf-8") as f:
    code = f.read()

# Target insertion point inside render_settings_view under col_p2
old_end = """            st.html(f"<div style='margin-top:20px; font-size:0.85rem; color:#64748B;'>Account ID: #{user['id']} | Role: {user['role'].upper()}</div>")"""

new_end = """            st.html(f"<div style='margin-top:20px; font-size:0.85rem; color:#64748B;'>Account ID: #{user['id']} | Role: {user['role'].upper()}</div>")

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
                        st.error(b_msg)"""

code_norm = code.replace("\r\n", "\n")
old_end_norm = old_end.replace("\r\n", "\n")
new_end_norm = new_end.replace("\r\n", "\n")

if old_end_norm in code_norm:
    code_norm = code_norm.replace(old_end_norm, new_end_norm, 1)
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(code_norm)
    print("SUCCESS: Patched modules/ui_views.py with DPDP privacy & backup controls")
else:
    print("WARNING: Old end block not found in modules/ui_views.py")
