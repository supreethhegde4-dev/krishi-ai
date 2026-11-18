"""
Patches modules/ui_views.py to display model provenance badges:
- 🟢 VALIDATED ON REAL AGRICULTURAL DATA (ICAR 2,200 empirical samples - 99.55% test accuracy) for Crop Recommendation
- 🟠 SYNTHETICALLY TRAINED MODEL (ICAR Agro-Climatic Regional Benchmarks) with regional baseline disclaimer for Crop Yield Prediction
"""
import os

views_path = os.path.join(os.path.dirname(__file__), "..", "modules", "ui_views.py")

with open(views_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Patch Crop Yield View
old_yield = """def render_crop_yield_view(user, farm):
    st.markdown("#### 🌾 Machine Learning Crop Yield Prediction")
    st.caption("Random Forest regressor trained on agro-climatic conditions to forecast harvest volume and benchmark against ICAR district standards.")"""

new_yield = """def render_crop_yield_view(user, farm):
    st.markdown("#### 🌾 Machine Learning Crop Yield Prediction")
    st.html("<div style='background:#FFFBEB; border:1px solid #FCD34D; border-radius:8px; padding:8px 12px; margin-bottom:12px; font-size:0.83rem; color:#92400E; display:flex; justify-content:space-between; align-items:center;'><span>🟠 <b>SYNTHETICALLY TRAINED MODEL</b> (ICAR Agro-Climatic Benchmarks)</span><span style='font-weight:600; color:#B45309;'>Scope: Estimated Regional Baseline Yield (Not Empirical Field Trial)</span></div>")
    st.caption("Random Forest regressor trained on agro-climatic conditions to forecast harvest volume and benchmark against ICAR district standards.")"""

# Handle both CRLF and LF
content = content.replace(old_yield.replace("\r\n", "\n"), new_yield.replace("\r\n", "\n"))
content = content.replace(old_yield.replace("\n", "\r\n"), new_yield.replace("\n", "\r\n"))

# 2. Patch Crop Recommendation View
old_crop = """        crop_res = recommend_crop(n_val, p_val, k_val, t_val, h_val, ph_val, r_val)
        st.html(f\"\"\"
        <div style="background-color:#F0FDF4; border:2px solid #0D5C3A; border-radius:10px; padding:18px; text-align:center; margin:14px 0;">
            <span style="background:#0D5C3A; color:white; padding:4px 12px; border-radius:12px; font-weight:700; font-size:0.8rem;">TOP AGRONOMIC MATCH</span>"""

new_crop = """        crop_res = recommend_crop(n_val, p_val, k_val, t_val, h_val, ph_val, r_val)
        prov_lbl = crop_res.get('model_provenance', 'VALIDATED ON REAL AGRICULTURAL DATA')
        st.html(f\"\"\"
        <div style="background-color:#F0FDF4; border:2px solid #0D5C3A; border-radius:10px; padding:18px; text-align:center; margin:14px 0;">
            <div style="margin-bottom:8px;">
                <span style="background:#0D5C3A; color:white; padding:4px 12px; border-radius:12px; font-weight:700; font-size:0.8rem;">TOP AGRONOMIC MATCH</span>
                <span style="background:#059669; color:white; padding:4px 10px; border-radius:12px; font-weight:700; font-size:0.75rem; margin-left:6px;">🟢 {prov_lbl}</span>
            </div>"""

content = content.replace(old_crop.replace("\r\n", "\n"), new_crop.replace("\r\n", "\n"))
content = content.replace(old_crop.replace("\n", "\r\n"), new_crop.replace("\n", "\r\n"))

with open(views_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully patched ui_views.py with model provenance badges.")
