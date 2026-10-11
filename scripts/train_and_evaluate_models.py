"""
Script: train_and_evaluate_models.py
Deskripsi: Melatih dan mengkomparasi multi-model Machine Learning:
- Random Forest Classifier (RF)
- HistGradientBoosting Classifier (LightGBM equivalent)
- Gradient Boosting Classifier (GBM)
- Support Vector Machine (SVM RBF)
- K-Nearest Neighbors (KNN)
- XGBoost & LightGBM (jika tersedia)
Menemukan model dengan akurasi tertinggi untuk klasifikasi LULC Jawa Timur.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import (
    RandomForestClassifier,
    HistGradientBoostingClassifier,
    GradientBoostingClassifier
)
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score, cohen_kappa_score, classification_report,
    confusion_matrix, f1_score, precision_score, recall_score
)

def train_and_evaluate():
    data_path = r"data\lulc_jatim\sentinel2_lulc_jatim.csv"
    out_dir = r"data\lulc_jatim"
    os.makedirs(out_dir, exist_ok=True)
    
    df = pd.read_csv(data_path)
    
    feature_cols = [
        "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12",
        "NDVI", "NDWI", "MNDWI", "NDBI", "BSI", "SAVI", "NDRE", "CMRI"
    ]
    
    X = df[feature_cols]
    y = df["class_code"]
    
    # 80:20 Train-Test Split dengan Stratified Sampling
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    class_names = [
        "Sawah", "Bangunan", "Mangrove", "Lahan Hijau",
        "Perairan Terbuka (Laut)", "Danau (Ranu-ranu)"
    ]
    
    split_info = {
        "total_samples": int(len(df)),
        "total_features": int(len(feature_cols)),
        "feature_names": feature_cols,
        "n_classes": len(class_names),
        "class_names": class_names,
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "train_samples_per_class": {class_names[k]: int(v) for k, v in y_train.value_counts().items()},
        "test_samples_per_class": {class_names[k]: int(v) for k, v in y_test.value_counts().items()}
    }
    
    # Daftar Model Kandidat
    models = {
        "Random Forest": RandomForestClassifier(
            n_estimators=200, max_depth=16, min_samples_split=3,
            random_state=42, n_jobs=-1
        ),
        "Hist Gradient Boosting": HistGradientBoostingClassifier(
            max_iter=200, max_depth=10, learning_rate=0.08,
            random_state=42
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=150, max_depth=5, learning_rate=0.08,
            random_state=42
        ),
        "Support Vector Machine (RBF)": Pipeline([
            ('scaler', StandardScaler()),
            ('svm', SVC(kernel='rbf', C=10.0, gamma='scale', probability=True, random_state=42))
        ]),
        "K-Nearest Neighbors (KNN)": Pipeline([
            ('scaler', StandardScaler()),
            ('knn', KNeighborsClassifier(n_neighbors=5, weights='distance'))
        ])
    }
    
    # Coba load XGBoost & LightGBM jika modul terinstal
    try:
        import xgboost as xgb
        models["XGBoost"] = xgb.XGBClassifier(
            n_estimators=180, max_depth=6, learning_rate=0.08,
            random_state=42, eval_metric='mlogloss', n_jobs=-1
        )
    except ImportError:
        pass
        
    try:
        import lightgbm as lgb
        models["LightGBM"] = lgb.LGBMClassifier(
            n_estimators=180, max_depth=6, learning_rate=0.08,
            random_state=42, n_jobs=-1, verbose=-1
        )
    except ImportError:
        pass
    
    results = {}
    best_acc = -1.0
    best_model_name = ""
    best_model_obj = None
    
    for name, model in models.items():
        print(f"Melatih: {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        kappa = cohen_kappa_score(y_test, y_pred)
        macro_f1 = f1_score(y_test, y_pred, average='macro')
        macro_prec = precision_score(y_test, y_pred, average='macro')
        macro_rec = recall_score(y_test, y_pred, average='macro')
        
        cm = confusion_matrix(y_test, y_pred).tolist()
        report = classification_report(y_test, y_pred, target_names=class_names, output_dict=True)
        
        results[name] = {
            "accuracy": round(float(acc), 4),
            "kappa": round(float(kappa), 4),
            "macro_f1": round(float(macro_f1), 4),
            "macro_precision": round(float(macro_prec), 4),
            "macro_recall": round(float(macro_rec), 4),
            "confusion_matrix": cm,
            "classification_report": report
        }
        
        print(f" -> {name} | Akurasi: {acc*100:.2f}% | Kappa: {kappa:.4f} | F1: {macro_f1:.4f}")
        
        if acc > best_acc:
            best_acc = acc
            best_model_name = name
            best_model_obj = model
            
    print(f"\n==========================================")
    print(f"MODEL DENGAN AKURASI TERTINGGI: {best_model_name} ({best_acc*100:.2f}%)")
    print(f"==========================================")
    
    # Feature Importance dari Random Forest
    rf_model = models["Random Forest"]
    importances = rf_model.feature_importances_
    feat_imp = sorted(
        [{"feature": f, "importance": round(float(imp), 4)} for f, imp in zip(feature_cols, importances)],
        key=lambda x: x["importance"], reverse=True
    )
    
    # Simpan Artefak
    best_model_path = os.path.join(out_dir, "best_lulc_model.pkl")
    joblib.dump(best_model_obj, best_model_path)
    
    rf_model_path = os.path.join(out_dir, "random_forest_lulc.pkl")
    joblib.dump(rf_model, rf_model_path)
    
    summary_data = {
        "split_info": split_info,
        "best_model_name": best_model_name,
        "best_model_accuracy": round(float(best_acc), 4),
        "best_model_kappa": results[best_model_name]["kappa"],
        "feature_importances": feat_imp,
        "model_comparison": results
    }
    
    metrics_path = os.path.join(out_dir, "model_comparison_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
        
    print(f"Model tersimpan di: {best_model_path}")
    print(f"Metrik tersimpan di: {metrics_path}")

if __name__ == "__main__":
    train_and_evaluate()
