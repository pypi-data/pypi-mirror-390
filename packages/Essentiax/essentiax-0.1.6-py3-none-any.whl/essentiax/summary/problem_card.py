import pandas as pd

def problem_card(df: pd.DataFrame):
    """
    Generates a quick 'Problem Card' summarizing dataset health.
    """

    print("\n✅ Generating Problem Card...")
    print("-" * 50)

    # 1. Shape
    print(f"[Essentia] 🔹 Shape: {df.shape}")

    # 2. Missing Values
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print("[Essentia] ✅ No Missing Values")
    else:
        print("[Essentia] ⚠️ Missing Values:")
        print(missing[missing > 0])

    # 3. Duplicates
    duplicates = df.duplicated().sum()
    if duplicates == 0:
        print("[Essentia] ✅ No Duplicates Found")
    else:
        print(f"[Essentia] ⚠️ Found {duplicates} Duplicate Rows")

    # 4. Numeric Columns Summary
    num_cols = df.select_dtypes(include=["int64", "float64"]).columns
    if len(num_cols) > 0:
        print("\n[Essentia] 🔍 Numeric Summary:")
        print(df[num_cols].describe().T)
    else:
        print("\n[Essentia] ℹ️ No Numeric Columns")

    # 5. Categorical Columns Summary
    cat_cols = df.select_dtypes(include=["object"]).columns
    if len(cat_cols) > 0:
        print("\n[Essentia] 🔍 Categorical Summary:")
        for col in cat_cols:
            top_values = df[col].value_counts().head(3)
            print(f"   {col}: {len(df[col].unique())} unique values")
            print(f"      Top values:\n{top_values}")
    else:
        print("\n[Essentia] ℹ️ No Categorical Columns")

    print("-" * 50)
    print("✅ Problem Card Completed.\n")
