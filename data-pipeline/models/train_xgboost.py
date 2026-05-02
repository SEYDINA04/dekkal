"""
Dëkkal — XGBoost Classifier Training v1.0
Dataset : dekkal_xgboost_training_dataset.csv
Method  : Leave-One-Out CV (40 samples)
Author  : Babacar Ndao
"""
import pandas as pd
import numpy as np
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.metrics import (accuracy_score, precision_score,
                             recall_score, f1_score, confusion_matrix,
                             classification_report)

# ── LOAD DATA ────────────────────────────────────────────
df = pd.read_csv('dekkal_xgboost_training_dataset.csv')

FEATURES = [
    'elevation_m', 'slope_deg',
    'clay_pct', 'sand_pct',
    'p95_mm_day', 'p99_mm_day',
    'sar_dry_km2', 'sar_wet_km2', 'sar_delta_km2',
    'soil_moisture', 'precip_mm'
]
TARGET = 'flood'

X = df[FEATURES]
y = df[TARGET]

print("Dataset :")
print(f"  Samples  : {len(df)}")
print(f"  flood=1  : {y.sum()}")
print(f"  flood=0  : {(y==0).sum()}")
print(f"  Features : {len(FEATURES)}")

# ── CLASS IMBALANCE ──────────────────────────────────────
# 30 flood=1 vs 10 flood=0 → scale_pos_weight
scale_pos_weight = (y==0).sum() / y.sum()
print(f"\nscale_pos_weight : {scale_pos_weight:.2f}")

# ── MODEL ────────────────────────────────────────────────
model = XGBClassifier(
    n_estimators     = 100,
    max_depth        = 3,
    learning_rate    = 0.1,
    scale_pos_weight = scale_pos_weight,
    eval_metric      = 'logloss',
    random_state     = 42,
    verbosity        = 0,
)

# ── LOO CROSS-VALIDATION ─────────────────────────────────
print("\nLeave-One-Out Cross-Validation...")
loo = LeaveOneOut()
y_pred = cross_val_predict(model, X, y, cv=loo)
y_prob = cross_val_predict(model, X, y, cv=loo, method='predict_proba')[:,1]

# ── METRICS ──────────────────────────────────────────────
acc  = accuracy_score(y, y_pred)
prec = precision_score(y, y_pred, zero_division=0)
rec  = recall_score(y, y_pred, zero_division=0)
f1   = f1_score(y, y_pred, zero_division=0)
cm   = confusion_matrix(y, y_pred)

print("\n" + "="*50)
print("LOO-CV RESULTS")
print("="*50)
print(f"  Accuracy  : {acc:.2%}")
print(f"  Precision : {prec:.2%}")
print(f"  Recall    : {rec:.2%}  ← target >80%")
print(f"  F1-Score  : {f1:.2%}  ← target >77%")
print(f"\nConfusion Matrix :")
print(f"  TN={cm[0,0]}  FP={cm[0,1]}")
print(f"  FN={cm[1,0]}  TP={cm[1,1]}")
print(f"\n{classification_report(y, y_pred, target_names=['No Flood','Flood'])}")

# ── TRAIN FINAL MODEL ON FULL DATASET ───────────────────
print("Training final model on full dataset...")
model.fit(X, y)

# ── FEATURE IMPORTANCE ───────────────────────────────────
importance = pd.Series(
    model.feature_importances_,
    index=FEATURES
).sort_values(ascending=False)

print("\nFeature Importance :")
print("="*50)
for feat, imp in importance.items():
    bar = "█" * int(imp * 40)
    print(f"  {feat:<20} {imp:.3f}  {bar}")

# ── SAVE MODEL ───────────────────────────────────────────
joblib.dump(model, 'dekkal_xgboost_v1.pkl')
joblib.dump(FEATURES, 'dekkal_xgboost_features.pkl')

print("\n✓ Modèle sauvegardé → dekkal_xgboost_v1.pkl")
print("✓ Features sauvegardées → dekkal_xgboost_features.pkl")

# ── PREDICTIONS SUR LE DATASET ───────────────────────────
df['flood_pred'] = y_pred
df['flood_prob'] = y_prob.round(3)
df['score_0_100'] = (y_prob * 100).round(0).astype(int)
df['correct'] = (df['flood_pred'] == df['flood']).astype(int)

print("\nPrédictions par zone :")
print("="*50)
for zone in df['zone'].unique():
    z = df[df['zone']==zone]
    zone_acc = z['correct'].mean()
    print(f"\n  {zone} (accuracy={zone_acc:.0%}) :")
    print(f"  {'Year':<6} {'Score':>6} {'Pred':>6} {'True':>6} {'OK':>4}")
    for _, r in z.iterrows():
        ok = "✓" if r['correct'] else "✗"
        print(f"  {int(r.year):<6} {int(r.score_0_100):>6} "
              f"{'flood' if r.flood_pred else 'safe':>6} "
              f"{'flood' if r.flood else 'safe':>6} {ok:>4}")

df.to_csv('dekkal_xgboost_predictions.csv', index=False)
print("\n✓ Prédictions → dekkal_xgboost_predictions.csv")
