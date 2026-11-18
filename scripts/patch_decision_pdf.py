import os

target_file = os.path.join(os.path.dirname(__file__), "..", "modules", "ui_views.py")

with open(target_file, "r", encoding="utf-8") as f:
    code = f.read()

# Add import
if "generate_unified_pdf_report" not in code:
    code = code.replace(
        "from modules.decision_engine import generate_unified_decision_report",
        "from modules.decision_engine import generate_unified_decision_report\nfrom modules.pdf_report_generator import generate_unified_pdf_report"
    )

# Replace the export buttons in render_decision_reports_view
old_buttons = """    # Export Buttons
    c_dl1, c_dl2 = st.columns([1, 1])
    with c_dl1:
        farmer_name = user.get("full_name", "Farmer Enterprise")
        farm_title = farm.get("farm_name", "Agricultural Enterprise")
        md_text = f"# Krishi AI Decision Brief - {r_crop}\\n\\nFarmer: {farmer_name}\\nFarm: {farm_title}\\n\\n## Recommendations:\\n" + "\\n".join(report.get("8_recommended_decisions", []))
        st.download_button(
            label="📥 Download Complete Decision Brief (TXT)",
            data=md_text,
            file_name=f"krishi_ai_brief_{r_crop}_{datetime.date.today()}.txt",
            mime="text/plain"
        )
    with c_dl2:
        if st.button("💾 Save Brief to User Audit Ledger", use_container_width=True):"""

new_buttons = """    # Export Buttons (PDF & TXT & Ledger)
    c_dl1, c_dl2, c_dl3 = st.columns([1.2, 1, 1])
    with c_dl1:
        try:
            pdf_bytes = generate_unified_pdf_report(report)
            st.download_button(
                label="📥 Download Official Executive Report (PDF)",
                data=pdf_bytes,
                file_name=f"krishi_ai_report_{r_crop}_{datetime.date.today()}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"PDF generation error: {e}")
    with c_dl2:
        farmer_name = user.get("full_name", "Farmer Enterprise")
        farm_title = farm.get("farm_name", "Agricultural Enterprise")
        md_text = f"# Krishi AI Decision Brief - {r_crop}\\n\\nFarmer: {farmer_name}\\nFarm: {farm_title}\\n\\n## Recommendations:\\n" + "\\n".join(report.get("8_recommended_decisions", []))
        st.download_button(
            label="📄 Download Summary (TXT)",
            data=md_text,
            file_name=f"krishi_ai_brief_{r_crop}_{datetime.date.today()}.txt",
            mime="text/plain",
            use_container_width=True
        )
    with c_dl3:
        if st.button("💾 Save to Account Ledger", use_container_width=True):"""

code_norm = code.replace("\r\n", "\n")
old_buttons_norm = old_buttons.replace("\r\n", "\n")
new_buttons_norm = new_buttons.replace("\r\n", "\n")

if old_buttons_norm in code_norm:
    code_norm = code_norm.replace(old_buttons_norm, new_buttons_norm, 1)
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(code_norm)
    print("SUCCESSFULLY PATCHED ui_views.py for PDF report export")
else:
    print("TARGET NOT FOUND in ui_views.py")
