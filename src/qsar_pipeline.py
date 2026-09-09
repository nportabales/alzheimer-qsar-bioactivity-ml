print("Installing tools...")
!pip install rdkit pandas xgboost scikit-learn seaborn matplotlib

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from rdkit import Chem
from rdkit.Chem import AllChem
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier

# ======================================================
# ALZHEIMER PROJECT - RESCUE AND DIAGNOSTIC SCRIPT
# ======================================================

# 2. LOAD DATA (WITH VALIDATION)
FILE_NAME = 'data/datos_alzheimer.csv'
print(f"\nLoading file: {FILE_NAME}")

try:
    # Attempt to read with semicolon separator (common in ChEMBL)
    df = pd.read_csv(FILE_NAME, sep=';')

    # Check 1: Were columns read correctly? Specifically 'Smiles'
    if 'Smiles' not in df.columns:
        print("ALERT: 'Smiles' column not found. Trying comma separator.")
        df = pd.read_csv(FILE_NAME, sep=',')

    print(f"   Detected columns: {list(df.columns)}")
    print(f"   Initial rows: {len(df)}")

    # 3. DATA CLEANING AND FILTERING
    # Select relevant columns
    df = df[['Molecule ChEMBL ID', 'Smiles', 'Standard Value', 'Standard Units', 'Standard Type']]

    # Filter for IC50 values and 'nM' units
    df = df[df['Standard Type'] == 'IC50']
    df = df[df['Standard Units'] == 'nM']

    # Drop rows with missing Smiles or Standard Value
    df = df.dropna(subset=['Smiles', 'Standard Value'])

    # Convert 'Standard Value' to numeric, handling potential comma decimal separators
    if df['Standard Value'].dtype == object:
         df['Standard Value'] = df['Standard Value'].astype(str).str.replace(',', '.').astype(float)

    print(f"Cleaned rows (IC50/nM): {len(df)}")

    # 4. COMPOUND CLASSIFICATION AND BALANCING
    def classify_compound(value):
        if value <= 1000: return 1 # Active
        elif value >= 10000: return 0 # Inactive
        return -1 # Undefined

    df['Class'] = df['Standard Value'].apply(classify_compound)
    df = df[df['Class'] != -1]

    # Balance the dataset to prevent class imbalance bias
    grouped = df.groupby('Class')
    min_samples = grouped.size().min()
    df_balanced = grouped.apply(lambda x: x.sample(min_samples, random_state=42)).reset_index(drop=True)

    print(f"Balanced Dataset: {len(df_balanced)} compounds ({min_samples} per class)")

    # 5. CHEMICAL FEATURIZATION (FINGERPRINT CALCULATION)
    print("\nCalculating Fingerprints (Morgan Fingerprints)...")

    def get_morgan_fingerprint(smiles):
        try:
            mol = Chem.MolFromSmiles(str(smiles)) # Ensure input is string
            if mol:
                # ECFP4, 1024 bits - a common choice for molecular fingerprints
                fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=1024)
                return np.array(fp)
            return None
        except Exception as e:
            # Log the error or handle invalid SMILES gracefully
            # print(f"Error processing SMILES {smiles}: {e}")
            return None

    # Apply fingerprint calculation and convert to list for DataFrame
    fingerprint_series = df_balanced['Smiles'].apply(get_morgan_fingerprint)

    # Remove entries where fingerprint calculation failed
    valid_indices = fingerprint_series.notna()
    df_final = df_balanced[valid_indices].copy()
    X_list = fingerprint_series[valid_indices].tolist()

    X = pd.DataFrame(X_list)
    y = df_final['Class']

    # Check 2: Verify that the feature matrix X is not empty or all zeros
    print(f"   Feature matrix X shape: {X.shape}")
    print(f"   Sum of values in X: {X.values.sum()} (If 0, something is wrong with fingerprints)")

    if X.values.sum() == 0:
        raise ValueError("CRITICAL ERROR! Fingerprints are all zeros. Please check the CSV file or SMILES data.")

    # 6. MACHINE LEARNING MODEL TRAINING
    print("\nTraining Machine Learning Models...")

    classifiers = {
        'K-Nearest Neighbors': KNeighborsClassifier(n_neighbors=5),
        'Support Vector Machine': SVC(kernel='rbf', random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'XGBoost': XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    }

    evaluation_results = []
    cv_splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    for name, clf_model in classifiers.items():
        # Create a preprocessing and classification pipeline
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('feature_selector', SelectKBest(score_func=f_classif, k=50)), # Select top K features
            ('classifier', clf_model)
        ])

        # Perform cross-validation and get mean scores
        accuracy = cross_val_score(pipeline, X, y, cv=cv_splitter, scoring='accuracy').mean()
        f1_score = cross_val_score(pipeline, X, y, cv=cv_splitter, scoring='f1').mean()

        print(f"   {name}: Accuracy = {accuracy:.4f}")
        evaluation_results.append({'Model': name, 'Accuracy': accuracy, 'F1-Score': f1_score})

    # 7. DISPLAY FINAL RESULTS
    results_df = pd.DataFrame(evaluation_results).sort_values(by='Accuracy', ascending=False)
    print("\nFINAL MODEL PERFORMANCE RESULTS:")
    print(results_df)

    # Plotting the results
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Model', y='Accuracy', data=results_df, hue='Model', legend=False, palette='viridis')
    plt.ylim(0.5, 1.0)
    plt.title('Model Accuracy - Alzheimer AChE Prediction')
    plt.xlabel('Machine Learning Model')
    plt.ylabel('Accuracy')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

except FileNotFoundError:
    print(f"\nERROR: The file '{FILE_NAME}' was not found. Please ensure it's in the correct directory.")
except Exception as e:
    print(f"\nAN UNEXPECTED ERROR OCCURRED: {e}")
    print("Please review the file name, data format, or other potential issues in the CSV.")
