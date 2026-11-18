"""
Crop Quality Assessment Engine for KisanAI.
Analyzes visual features, color ripeness, firmness, and surface defects to assign
Quality Score (0-100), APMC Grade (Grade A / FAQ / Non-FAQ), and Price Multiplier.
"""
from PIL import Image
import numpy as np
from typing import Dict, Any, Optional, Tuple


def analyze_crop_image(image: Image.Image) -> Dict[str, Any]:
    """
    Performs computer vision color and texture heuristics on uploaded crop photo.
    """
    img_rgb = image.convert('RGB').resize((150, 150))
    arr = np.array(img_rgb).astype(float)
    
    # Calculate RGB channel means
    r_mean = float(np.mean(arr[:, :, 0]))
    g_mean = float(np.mean(arr[:, :, 1]))
    b_mean = float(np.mean(arr[:, :, 2]))
    
    # Redness Index (for tomatoes and fruits)
    redness_ratio = (r_mean / (g_mean + b_mean + 1e-5)) * 2.0
    
    # Surface Uniformity / Texture Variance
    gray = 0.2989 * arr[:, :, 0] + 0.5870 * arr[:, :, 1] + 0.1140 * arr[:, :, 2]
    variance = float(np.var(gray))
    # High local variance indicates spots, blemishes, or bruising
    defect_indicator = min(25.0, round(variance / 200.0, 1))

    return {
        "r_mean": round(r_mean, 1),
        "g_mean": round(g_mean, 1),
        "b_mean": round(b_mean, 1),
        "redness_index": round(redness_ratio, 2),
        "estimated_defect_pct": defect_indicator,
        "is_analyzed": True
    }


def evaluate_quality(
    crop_name: str,
    firmness: str = "Firm (Optimal)",      # Firm (Optimal), Medium, Soft/Overripe
    defect_pct: float = 3.0,              # 0% to 30%
    size_uniformity: str = "High (>85%)",  # High, Medium, Mixed
    color_maturity: str = "Ripe (Red)",   # Green, Turning, Pink, Ripe (Red), Overripe
    uploaded_image: Optional[Image.Image] = None
) -> Dict[str, Any]:
    """
    Deterministic scoring and grading based on physical attributes and optional image.
    """
    base_score = 100.0

    # 1. Defect deduction
    defect_deduction = defect_pct * 1.5
    base_score -= defect_deduction

    # 2. Firmness scoring
    if "Firm" in firmness:
        firmness_score = 0.0
    elif "Medium" in firmness:
        firmness_score = -10.0
    else:  # Soft/Overripe
        firmness_score = -25.0
    base_score += firmness_score

    # 3. Size Uniformity
    if "High" in size_uniformity:
        uniformity_bonus = 5.0
    elif "Medium" in size_uniformity:
        uniformity_bonus = 0.0
    else:
        uniformity_bonus = -8.0
    base_score += uniformity_bonus

    # 4. Color Maturity
    if "Ripe" in color_maturity or "Pink" in color_maturity:
        color_bonus = 0.0
    elif "Turning" in color_maturity:
        color_bonus = -3.0  # Needs couple days
    elif "Overripe" in color_maturity:
        color_bonus = -15.0
    else:  # Green
        color_bonus = -10.0
    base_score += color_bonus

    # 5. Optional Image Adjustment
    img_data = None
    if uploaded_image is not None:
        try:
            img_data = analyze_crop_image(uploaded_image)
            if img_data["estimated_defect_pct"] > 15.0:
                base_score -= 5.0
            elif img_data["redness_index"] > 1.2:
                base_score += 3.0
        except Exception:
            pass

    final_score = max(20.0, min(100.0, round(base_score, 1)))

    # Grade determination
    if final_score >= 85.0:
        grade = "Grade A (Premium)"
        price_multiplier = 1.08  # +8% premium
        shelf_life_days = 7
        badge_color = "#2e7d32"
        description = "Export and supermarket quality: Vibrant color, excellent firmness, minimal blemishes (<4%)."
    elif final_score >= 65.0:
        grade = "FAQ (Fair Average Quality)"
        price_multiplier = 1.00  # Standard APMC benchmark
        shelf_life_days = 4
        badge_color = "#1565c0"
        description = "Standard wholesale market quality: Good commercial acceptability, minor cosmetic spots."
    else:
        grade = "Non-FAQ (Substandard / Processing)"
        price_multiplier = 0.82  # -18% discount
        shelf_life_days = 2
        badge_color = "#c62828"
        description = "Suitable only for local juice/ketchup processing. Significant softness or surface damage."

    return {
        "crop_name": crop_name,
        "quality_score": final_score,
        "grade": grade,
        "price_multiplier": price_multiplier,
        "premium_discount_pct": round((price_multiplier - 1.0) * 100.0, 1),
        "shelf_life_ambient_days": shelf_life_days,
        "shelf_life_cold_chain_days": shelf_life_days * 3,
        "badge_color": badge_color,
        "description": description,
        "image_analysis": img_data
    }
