"""
smartEDA.py
===============================
Essentia Smart Exploratory Data Analysis

Automatically analyzes ANY dataset and provides comprehensive insights.
Optimized for large datasets.
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def smart_eda(df: pd.DataFrame, sample_size: int = None) -> None:
    """
    Perform comprehensive Exploratory Data Analysis on any dataset.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataset to analyze
    sample_size : int, optional
        For large datasets, analyze only a sample (None = full dataset)
    
    Returns:
    --------
    None (prints analysis to console)
    """
    
    print("\n🧠 Starting Essentia Smart EDA...")
    print("="*60)
    
    # Use sample for very large datasets
    original_rows = len(df)
    if sample_size and len(df) > sample_size:
        print(f"📊 Large dataset detected. Using sample of {sample_size:,} rows")
        df_sample = df.sample(n=sample_size, random_state=42)
        print(f"   (Original: {original_rows:,} rows)\n")
    else:
        df_sample = df
    
    # ═══════════════════════════════════════════════════════
    # 1️⃣ BASIC INFORMATION
    # ═══════════════════════════════════════════════════════
    print("📋 [1/6] BASIC INFORMATION")
    print("-"*60)
    print(f"   • Dataset Shape:      {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"   • Memory Usage:       {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print(f"   • Total Cells:        {df.shape[0] * df.shape[1]:,}")
    print(f"   • Duplicate Rows:     {df.duplicated().sum():,} ({100*df.duplicated().sum()/len(df):.2f}%)")
    
    # ═══════════════════════════════════════════════════════
    # 2️⃣ COLUMN INFORMATION
    # ═══════════════════════════════════════════════════════
    print("\n📊 [2/6] COLUMN TYPES & DATA TYPES")
    print("-"*60)
    
    # Data type breakdown
    dtype_counts = df.dtypes.value_counts()
    print("   Data Type Distribution:")
    for dtype, count in dtype_counts.items():
        print(f"      • {dtype}: {count} columns")
    
    # Numeric vs Categorical
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    datetime_cols = df.select_dtypes(include=['datetime64']).columns
    
    print(f"\n   Column Categories:")
    print(f"      • Numeric:       {len(numeric_cols)} columns")
    print(f"      • Categorical:   {len(categorical_cols)} columns")
    print(f"      • DateTime:      {len(datetime_cols)} columns")
    
    # ═══════════════════════════════════════════════════════
    # 3️⃣ MISSING VALUES ANALYSIS
    # ═══════════════════════════════════════════════════════
    print("\n⚠️  [3/6] MISSING VALUES ANALYSIS")
    print("-"*60)
    
    missing = df.isnull().sum()
    missing_pct = 100 * missing / len(df)
    missing_df = pd.DataFrame({
        'Missing_Count': missing,
        'Missing_Percent': missing_pct
    })
    missing_df = missing_df[missing_df['Missing_Count'] > 0].sort_values('Missing_Count', ascending=False)
    
    if len(missing_df) > 0:
        print(f"   ⚠️  Found {missing.sum():,} missing values across {len(missing_df)} columns")
        print("\n   Top 10 Columns with Missing Values:")
        for idx, (col, row) in enumerate(missing_df.head(10).iterrows(), 1):
            print(f"      {idx:2d}. {col:20s} → {int(row['Missing_Count']):8,} missing ({row['Missing_Percent']:.2f}%)")
    else:
        print("   ✅ No missing values found!")
    
    # ═══════════════════════════════════════════════════════
    # 4️⃣ NUMERIC COLUMNS ANALYSIS
    # ═══════════════════════════════════════════════════════
    if len(numeric_cols) > 0:
        print("\n📈 [4/6] NUMERIC COLUMNS ANALYSIS")
        print("-"*60)
        print(f"   Analyzing {len(numeric_cols)} numeric columns...\n")
        
        # Statistical summary
        desc = df_sample[numeric_cols].describe()
        print("   Statistical Summary (first 5 columns):")
        print(desc.iloc[:, :5].to_string())
        
        # Potential outliers detection
        print("\n   🎯 Potential Outliers (using IQR method):")
        outlier_info = []
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            outliers = ((df[col] < lower) | (df[col] > upper)).sum()
            if outliers > 0:
                outlier_info.append((col, outliers, 100*outliers/len(df)))
        
        if outlier_info:
            outlier_info.sort(key=lambda x: x[1], reverse=True)
            for col, count, pct in outlier_info[:10]:
                print(f"      • {col:20s} → {count:8,} outliers ({pct:.2f}%)")
        else:
            print("      ✅ No significant outliers detected")
        
        # Skewness analysis
        print("\n   📊 Skewness Analysis (top 5 skewed columns):")
        skewness = df_sample[numeric_cols].skew().sort_values(ascending=False)
        for col, skew in skewness.head(5).items():
            skew_type = "Right-skewed" if skew > 1 else "Left-skewed" if skew < -1 else "Normal"
            print(f"      • {col:20s} → {skew:7.2f} ({skew_type})")
    
    # ═══════════════════════════════════════════════════════
    # 5️⃣ CATEGORICAL COLUMNS ANALYSIS
    # ═══════════════════════════════════════════════════════
    if len(categorical_cols) > 0:
        print("\n🏷️  [5/6] CATEGORICAL COLUMNS ANALYSIS")
        print("-"*60)
        print(f"   Analyzing {len(categorical_cols)} categorical columns...\n")
        
        for col in categorical_cols[:10]:  # Show first 10 categorical columns
            unique_count = df[col].nunique()
            top_values = df[col].value_counts().head(3)
            
            print(f"   📌 {col}")
            print(f"      • Unique Values: {unique_count:,}")
            print(f"      • Top 3 Values:")
            for val, count in top_values.items():
                print(f"         - {val}: {count:,} ({100*count/len(df):.2f}%)")
            print()
        
        if len(categorical_cols) > 10:
            print(f"   ... and {len(categorical_cols) - 10} more categorical columns")
    
    # ═══════════════════════════════════════════════════════
    # 6️⃣ CORRELATIONS (for numeric columns)
    # ═══════════════════════════════════════════════════════
    if len(numeric_cols) > 1:
        print("\n🔗 [6/6] CORRELATION ANALYSIS")
        print("-"*60)
        
        # Compute correlation matrix
        corr_matrix = df_sample[numeric_cols].corr()
        
        # Find high correlations (excluding diagonal)
        print("   🔍 High Correlations (|correlation| > 0.7):")
        high_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    high_corr.append((
                        corr_matrix.columns[i],
                        corr_matrix.columns[j],
                        corr_val
                    ))
        
        if high_corr:
            high_corr.sort(key=lambda x: abs(x[2]), reverse=True)
            for col1, col2, corr in high_corr[:10]:
                corr_type = "Positive" if corr > 0 else "Negative"
                print(f"      • {col1:15s} ↔ {col2:15s} → {corr:6.3f} ({corr_type})")
        else:
            print("      ℹ️  No strong correlations found")
    
    # ═══════════════════════════════════════════════════════
    # FINAL SUMMARY
    # ═══════════════════════════════════════════════════════
    print("\n" + "="*60)
    print("✅ SMART EDA COMPLETED!")
    print("="*60)
    
    print("\n💡 Key Insights:")
    print(f"   • Dataset has {df.shape[0]:,} rows and {df.shape[1]} columns")
    print(f"   • Missing values: {missing.sum():,} ({100*missing.sum()/(df.shape[0]*df.shape[1]):.2f}% of total)")
    print(f"   • Duplicates: {df.duplicated().sum():,} rows")
    
    if len(numeric_cols) > 0:
        print(f"   • Numeric columns: {len(numeric_cols)} (ready for ML)")
    if len(categorical_cols) > 0:
        print(f"   • Categorical columns: {len(categorical_cols)} (may need encoding)")
    
    print("\n📊 Recommended Next Steps:")
    if missing.sum() > 0:
        print("   1. Handle missing values (use smart_clean)")
    if len([x for x in outlier_info if x[1] > 0]) > 0 if 'outlier_info' in locals() else False:
        print("   2. Remove or cap outliers")
    if len(categorical_cols) > 0:
        print("   3. Encode categorical features")
    if len(numeric_cols) > 0:
        print("   4. Scale numeric features")
    
    print("\n" + "="*60 + "\n")


# ═══════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    # Test with sample data
    print("🧪 Testing Smart EDA with sample data...\n")
    
    # Create sample dataset
    np.random.seed(42)
    data = {
        'Age': np.random.randint(18, 80, 1000),
        'Salary': np.random.randint(30000, 150000, 1000),
        'Score': np.random.normal(75, 15, 1000),
        'City': np.random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai'], 1000),
        'Department': np.random.choice(['IT', 'HR', 'Finance', 'Sales'], 1000),
        'Experience': np.random.randint(0, 30, 1000)
    }
    
    # Add some missing values
    df = pd.DataFrame(data)
    df.loc[np.random.choice(df.index, 50), 'Salary'] = np.nan
    df.loc[np.random.choice(df.index, 30), 'City'] = np.nan
    
    # Add some outliers
    df.loc[np.random.choice(df.index, 10), 'Salary'] = 500000
    
    # Run EDA
    smart_eda(df)