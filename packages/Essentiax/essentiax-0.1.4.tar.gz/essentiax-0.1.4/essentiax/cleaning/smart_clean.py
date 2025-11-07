"""
smart_clean.py
===============================
Essentia Universal Smart Data Cleaner

Automatically cleans, scales, and encodes datasets.
Works with ANY dataset (CSV, Excel, JSON, etc.)
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder

def smart_clean(
    df: pd.DataFrame,
    handle_missing: bool = True,
    remove_outliers: bool = True,
    scale_numeric: bool = True,
    encode_categorical: bool = True,
    inplace: bool = False
) -> pd.DataFrame:
    """
    Clean and preprocess any dataset automatically.
    Returns an ML-ready DataFrame.

    Parameters:
    -----------
    df : pd.DataFrame
        Input dataset
    handle_missing : bool
        Fill or drop missing values
    remove_outliers : bool
        Remove outliers using IQR
    scale_numeric : bool
        Apply StandardScaler to numeric columns
    encode_categorical : bool
        Apply OneHotEncoding to categorical columns
    inplace : bool
        Modify original dataframe (False = return new)
    """

    if not inplace:
        df = df.copy()

    print("\n🧹 Starting Essentia Smart Clean Process...")
    print("="*60)

    # 1️⃣ Handle Missing Values
    if handle_missing:
        print("🔧 Handling missing values...")
        for col in df.columns:
            if df[col].isnull().sum() > 0:
                if df[col].dtype in ['int64', 'float64']:
                    df[col].fillna(df[col].median(), inplace=True)
                else:
                    df[col].fillna(df[col].mode()[0], inplace=True)
        print("✅ Missing values handled.")

    # 2️⃣ Remove Outliers (IQR Method)
    if remove_outliers:
        print("🧮 Removing outliers using IQR...")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            df = df[(df[col] >= lower) & (df[col] <= upper)]
        print("✅ Outliers removed.")

    # 3️⃣ Scale Numeric Columns
    if scale_numeric:
        print("⚖️ Scaling numeric features...")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            scaler = StandardScaler()
            df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
            print(f"✅ Scaled {len(numeric_cols)} numeric columns.")
        else:
            print("⚠️ No numeric columns to scale.")

    # 4️⃣ Encode Categorical Columns
    if encode_categorical:
        print("🎨 Encoding categorical features...")
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(cat_cols) > 0:
            df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
            print(f"✅ Encoded {len(cat_cols)} categorical columns.")
        else:
            print("⚠️ No categorical columns to encode.")

    # 5️⃣ Summary
    print("="*60)
    print("🎯 Cleaning Summary:")
    print(f"✅ Final Shape: {df.shape}")
    print(f"✅ Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print("="*60)

    return df
