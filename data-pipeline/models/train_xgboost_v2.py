"""
Dëkkal — XGBoost v2 — Sans features SAR
Features SAR utiles pour labels mais pas pour inférence point-level
Author : Babacar Ndao
"""
import pandas as pd
import numpy as np
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.metrics import (accuracy_score, precision_score,
                             recall_score, f1_score, confusion_matrix)

df = pd.read_csv('dekkal_xgboost_training_dataset.csv')

# Features sans SAR — disponibles à l'échelle d'une adresse
FEATURES_V2 = [
    'elevation_m',
    'slope_deg',
    'clay_pct',
    'p95_mm_day',
    'p99_mm_day',
    'soil_moisture',
    'precip_mm',
]
TARGET = 'flood'

X = df[FEATURES_V2]
y = df[TARGET]

scale_pos_weight = (y==0).sum() / y.sum()

model = XGBClassifier(
    n_estimators     = 100,
    max_depth        = 3,
    learning_rate    = 0.1,
    scale_pos_weight = scale_pos_weight,
    eval_metric      = 'logloss',
    random_state     = 42,
    verbosity        = 0,
)

loo    = LeaveOneOut()
y_pred = cross_val_predict(model, X, y, cv=loo)
y_prob = cross_val_predict(model, X, y, cv=loo,
                           method='predict_proba')[:,1]

acc  = accuracy_score(y, y_pred)
prec = precision_score(y, y_pred, zero_division=0)
rec  = recall_score(y, y_pred, zero_division=0)
f1   = f1_score(y, y_pred, zero_division=0)
cm   = confusion_matrix(y, y_pred)

print("XGBoost v2 — No SAR features")
print("="*50)
print(f"  Accuracy  : {acc:.2%}")
print(f"  Precision : {prec:.2%}")
print(f"  Recall    : {rec:.2%}")
print(f"  F1-Score  : {f1:.2%}")
print(f"\n  TN={cm[0,0]}  FP={cm[0,1]}")
print(f"  FN={cm[1,0]}  TP={cm[1,1]}")

model.fit(X, y)

importance = pd.Series(
    model.feature_importances_,
    index=FEATURES_V2
).sort_values(ascending=False)

print("\nFeature Importance :")
for feat, imp in importance.items():
    bar = "█" * int(imp * 40)
    print(f"  {feat:<20} {imp:.3f}  {bar}")

joblib.dump(model,       'dekkal_xgboost_v2.pkl')
joblib.dump(FEATURES_V2, 'dekkal_xgboost_features_v2.pkl')
print("\n✓ Modèle v2 → dekkal_xgboost_v2.pkl")
