import pandas as pd
import os
import csv
import requests
from io import StringIO

def smart_read(path, dropna=False, fillna=None):
    """
    Smart CSV/Excel Reader with:
    - Automatic delimiter detection (for CSV)
    - URL and local file support
    - Missing value handling (dropna/fillna)
    - Data type and shape inspection
    - Quick dataset overview (mini-EDA)

    Args:
        path (str): File path or URL (.csv or .xlsx)
        dropna (bool): If True, drops rows with missing values
        fillna (any): Value to fill missing cells (e.g., 0, "Unknown")

    Returns:
        pd.DataFrame or None
    """
    try:
        print(f"[Essentiax] 📂 Reading file: {path}")

        # 🔹 Detect URL
        if path.startswith("http://") or path.startswith("https://"):
            response = requests.get(path)
            if response.status_code != 200:
                print(f"[Essentiax] ❌ Failed to fetch URL. Status: {response.status_code}")
                return None
            data = StringIO(response.text)
            try:
                # Try reading as CSV first
                df = pd.read_csv(data)
                print(f"[Essentiax] ✅ File loaded from URL (CSV) successfully! Shape: {df.shape}")
            except Exception:
                df = pd.read_excel(data)
                print(f"[Essentiax] ✅ File loaded from URL (Excel) successfully! Shape: {df.shape}")

        else:
            # 🔹 Local file mode
            ext = os.path.splitext(path)[1].lower()

            if not os.path.exists(path):
                print(f"[Essentiax] ❌ File not found: {path}")
                return None

            if ext == ".csv":
                with open(path, 'r', encoding='utf-8') as f:
                    sample = f.read(2048)
                    sniffer = csv.Sniffer()
                    delimiter = sniffer.sniff(sample).delimiter
                    print(f"[Essentiax] Detected delimiter: '{delimiter}'")

                df = pd.read_csv(path, delimiter=delimiter)

            elif ext in [".xls", ".xlsx"]:
                df = pd.read_excel(path)

            else:
                print("[Essentiax] ❌ Unsupported file type. Use CSV or Excel.")
                return None

        # 🔹 Data Overview
        print(f"[Essentiax] ✅ Loaded successfully with shape {df.shape}")
        print("[Essentiax] Column Data Types:")
        print(df.dtypes)

        # 🔹 Missing value detection
        missing = df.isnull().sum()
        missing_cols = missing[missing > 0]

        if not missing_cols.empty:
            print("[Essentiax] ⚠ Missing Values Found:")
            print(missing_cols)

            if dropna:
                df = df.dropna()
                print("[Essentiax] 🧹 Dropped rows with missing values.")
            elif fillna is not None:
                df = df.fillna(fillna)
                print(f"[Essentiax] 🧹 Filled missing values with '{fillna}'.")
        else:
            print("[Essentiax] ✅ No Missing Values Found.")

        # 🔹 Quick Mini-EDA
        print("\n[Essentiax] 🔍 Quick Dataset Overview")
        print("--------------------------------------------------")
        print("[Essentiax] 🔹 First 5 Rows:")
        print(df.head())
        print("--------------------------------------------------")
        print("[Essentiax] 🔹 Shape:", df.shape)
        print("[Essentiax] 🔹 Columns:", list(df.columns))
        print("--------------------------------------------------")
        print("[Essentiax] 🔹 Descriptive Statistics:")
        print(df.describe(include='all'))
        print("--------------------------------------------------")

        return df

    except Exception as e:
        print(f"[Essentiax] ❌ Error reading file: {e}")
        return None
