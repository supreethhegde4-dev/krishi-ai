import os
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, r2_score, mean_absolute_error, mean_squared_error

print("=== MACHINE LEARNING MODEL AUDIT ===")

# 1. Crop Recommendation Model
crop_path = "models/crop_recommendation_model.pkl"
if os.path.exists(crop_path):
    crop_bundle = joblib.load(crop_path)
    clf = crop_bundle["model"]
    features = crop_bundle["features"]
    crops = crop_bundle["crops"]
    print("\n[1] Crop Recommendation Model:")
    print(f"  Estimator: {type(clf).__name__}")
    print(f"  n_estimators: {clf.n_estimators}, max_depth: {clf.max_depth}")
    print(f"  Features expected ({len(features)}): {features}")
    print(f"  Crops supported ({len(crops)}): {crops}")
    
    # Feature importances
    imp = dict(zip(features, clf.feature_importances_))
    sorted_imp = sorted(imp.items(), key=lambda x: x[1], reverse=True)
    print("  Feature Importances:")
    for f_name, val in sorted_imp:
        print(f"    - {f_name:12}: {val*100:.1f}%")
else:
    print(f"[1] Crop model {crop_path} NOT FOUND")

# 2. Yield Prediction Model
yield_path = "models/yield_prediction_model.pkl"
if os.path.exists(yield_path):
    yield_bundle = joblib.load(yield_path)
    reg = yield_bundle["model"]
    feat_cols = yield_bundle["features"]
    le = yield_bundle["label_encoder"]
    print("\n[2] Harvest Yield Prediction Model:")
    print(f"  Estimator: {type(reg).__name__}")
    print(f"  n_estimators: {reg.n_estimators}, max_depth: {reg.max_depth}")
    print(f"  Features expected ({len(feat_cols)}): {feat_cols}")
    print(f"  Target: yield_per_acre_quintals")
    
    # Feature importances
    imp = dict(zip(feat_cols, reg.feature_importances_))
    sorted_imp = sorted(imp.items(), key=lambda x: x[1], reverse=True)
    print("  Feature Importances:")
    for f_name, val in sorted_imp:
        print(f"    - {f_name:12}: {val*100:.1f}%")
else:
    print(f"[2] Yield model {yield_path} NOT FOUND")
